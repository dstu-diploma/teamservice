from typing import Awaitable, Callable, Protocol


class IEventConsumerPort(Protocol):
    async def consume(
        self,
        routing_keys: list[str],
        handler: Callable[[dict], Awaitable[None]],
    ) -> None: ...
