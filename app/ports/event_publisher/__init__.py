from pydantic import BaseModel
from typing import Protocol


class IEventPublisherPort(Protocol):
    async def connect(self) -> None: ...
    async def publish(self, event_name: str, data: BaseModel) -> None: ...
