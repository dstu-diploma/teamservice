from pydantic import BaseModel
from typing import Protocol


class IEventPublisherPort(Protocol):
    async def connect(self) -> None: ...
    async def publish(
        self, routing_key: str, event_name, data: BaseModel
    ) -> None: ...
