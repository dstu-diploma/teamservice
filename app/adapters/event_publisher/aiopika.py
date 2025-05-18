from app.ports.event_publisher import IEventPublisherPort
from pydantic import BaseModel
from uuid import uuid4
import aio_pika

from app.ports.event_publisher.dto import EventPayload
from app.ports.event_publisher.exceptions import (
    EventPublisherNotConnectedException,
)


class AioPikaEventPublisherAdapter(IEventPublisherPort):
    def __init__(self, connection_url: str, exchange_name: str = "events"):
        self.connection_url = connection_url
        self.exchange_name = exchange_name
        self._exchange = None
        self._channel = None

    async def connect(self):
        connection = await aio_pika.connect_robust(self.connection_url)
        self._channel = await connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC
        )

    async def publish(self, event_name: str, data: BaseModel) -> None:
        if not self._exchange:
            raise EventPublisherNotConnectedException()

        payload = EventPayload(
            event_id=uuid4(), event_name=event_name, data=data.model_dump()
        )

        message = aio_pika.Message(
            body=payload.model_dump_json().encode(),
            content_type="application/json",
        )

        await self._exchange.publish(message, routing_key=event_name)
