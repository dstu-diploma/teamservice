from typing import Awaitable, Callable, Protocol
import asyncio


class IEventConsumerPort(Protocol):
    async def connect(self) -> None: ...
    async def create_consuming_loop(
        self,
        routing_keys: list[str],
        handler: Callable[[dict], Awaitable[None]],
    ) -> asyncio.Task: ...
