from __future__ import annotations

import asyncio
import logging
import random
from collections import OrderedDict
from typing import Callable, Literal, Sequence, overload

from openai import AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

from .deployment import (
    AzureDeployment,
    Deployment,
    OpenAIDeployment,
)

logger = logging.getLogger(__name__)


class SwitchboardError(Exception):
    pass


def two_random_choices(model: str, options: list[Deployment]) -> Deployment:
    """Power of two random choices algorithm.

    Randomly select 2 deployments and return the one
    with lower util for the given model.
    """
    selected = random.sample(options, min(2, len(options)))
    return min(selected, key=lambda d: d.util(model))


class Switchboard:
    def __init__(
        self,
        deployments: Sequence[AzureDeployment | OpenAIDeployment],
        selector: Callable[[str, list[Deployment]], Deployment] = two_random_choices,
        failover_policy: AsyncRetrying = AsyncRetrying(stop=stop_after_attempt(2)),
    ) -> None:
        self.deployments: dict[str, Deployment] = {}
        self.fallback: Deployment | None = None

        if not deployments:
            raise SwitchboardError("No deployments provided")

        for deployment in deployments:
            if isinstance(deployment, OpenAIDeployment):
                self.fallback = Deployment(deployment)
            else:
                self.deployments[deployment.name] = Deployment(deployment)

        self.selector = selector

        self.failover_policy = failover_policy

        # expire old sessions
        self._sessions = _LRUDict(max_size=1024)

        # reset usage every minute
        self._ratelimit_window = 60.0

    async def __aenter__(self) -> Switchboard:
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.stop()

    def start(self) -> None:
        async def periodic_reset():
            while True:
                await asyncio.sleep(self._ratelimit_window)
                logger.debug("Resetting usage counters")
                self.reset_usage()

        self.ratelimit_reset_task = asyncio.create_task(periodic_reset())

    async def stop(self):
        if self.ratelimit_reset_task:
            try:
                self.ratelimit_reset_task.cancel()
                await self.ratelimit_reset_task
            except asyncio.CancelledError:
                pass

    def reset_usage(self) -> None:
        for client in self.deployments.values():
            client.reset_usage()

    def get_usage(self) -> dict[str, dict]:
        return {name: client.get_usage() for name, client in self.deployments.items()}

    def select_deployment(
        self, *, model: str, session_id: str | None = None
    ) -> Deployment:
        """
        Select a deployment using the power of two random choices algorithm.
        If session_id is provided, try to use that specific deployment first.
        """
        # Handle session-based routing first
        if session_id and session_id in self._sessions:
            client = self._sessions[session_id]
            if client.is_healthy(model):
                logger.debug(f"Reusing {client} for session {session_id}")
                return client

            logger.warning(f"{client} is unhealthy, falling back to selection")

        # Get eligible deployments for the requested model
        eligible_deployments = list(
            filter(lambda d: d.is_healthy(model), self.deployments.values())
        )
        if not eligible_deployments:
            raise SwitchboardError(f"No eligible deployments available for {model}")

        if len(eligible_deployments) == 1:
            return eligible_deployments[0]

        selection = self.selector(model, eligible_deployments)
        logger.debug(f"Selected {selection}")

        if session_id:
            self._sessions[session_id] = selection

        return selection

    @overload
    async def create(
        self, *, session_id: str | None = None, stream: Literal[True], **kwargs
    ) -> AsyncStream[ChatCompletionChunk]: ...

    @overload
    async def create(
        self, *, session_id: str | None = None, **kwargs
    ) -> ChatCompletion: ...

    async def create(
        self,
        *,
        model: str,
        session_id: str | None = None,
        stream: bool = False,
        **kwargs,
    ) -> ChatCompletion | AsyncStream[ChatCompletionChunk]:
        """
        Send a chat completion request to the selected deployment, with automatic fallback.
        """

        try:
            async for attempt in self.failover_policy:
                with attempt:
                    client = self.select_deployment(model=model, session_id=session_id)
                    logger.debug(f"Sending completion request to {client}")
                    response = await client.create(model=model, stream=stream, **kwargs)
                    return response
        except RetryError:
            logger.exception("Azure failovers exhausted")

        if self.fallback:
            logger.warning("Attempting fallback to OpenAI")
            try:
                return await self.fallback.create(model=model, stream=stream, **kwargs)
            except Exception as e:
                raise SwitchboardError("Fallback to OpenAI failed") from e
        else:
            raise SwitchboardError("All attempts failed")

    def __repr__(self) -> str:
        return f"Switchboard({self.deployments})"


# borrowed from https://gist.github.com/davesteele/44793cd0348f59f8fadd49d7799bd306
class _LRUDict(OrderedDict):
    def __init__(self, *args, max_size: int = 1024, **kwargs):
        assert max_size > 0
        self.max_size = max_size

        super().__init__(*args, **kwargs)

    def __setitem__(self, key: str, value: Deployment) -> None:
        super().__setitem__(key, value)
        super().move_to_end(key)

        while len(self) > self.max_size:  # pragma: no cover
            oldkey = next(iter(self))
            super().__delitem__(oldkey)

    def __getitem__(self, key: str) -> Deployment:
        val = super().__getitem__(key)
        super().move_to_end(key)

        return val
