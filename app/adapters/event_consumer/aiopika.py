from app.ports.event_consumer import IEventConsumerPort
from typing import Callable, Awaitable
import aio_pika
import json


class AioPikaEventConsumerAdapter(IEventConsumerPort):
    def __init__(
        self,
        connection_url: str,
        exchange_name: str = "events",
        queue_name: str = "",
        dlx_name: str = "dlx",
    ):
        self.connection_url = connection_url
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.dlx_name = dlx_name

        self._connection = None
        self._channel = None
        self._exchange = None
        self._queue = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(self.connection_url)
        self._channel = await self._connection.channel()

        self._exchange = await self._channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC
        )

        dlx = await self._channel.declare_exchange(
            self.dlx_name, aio_pika.ExchangeType.FANOUT
        )

        self._queue = await self._channel.declare_queue(
            self.queue_name or "",
            durable=True,
            arguments={"x-dead-letter-exchange": self.dlx_name},
        )

        # DLQ queue
        dlq_queue = await self._channel.declare_queue(
            f"{self.queue_name}_dlq", durable=True
        )
        await dlq_queue.bind(dlx)

    async def consume(
        self,
        routing_keys: list[str],
        handler: Callable[[dict], Awaitable[None]],
    ) -> None:
        if not self._exchange or not self._queue:
            raise RuntimeError("You must call connect() before consume()")

        for key in routing_keys:
            await self._queue.bind(self._exchange, routing_key=key)

        async def on_message(message: aio_pika.abc.AbstractIncomingMessage):
            async with message.process(requeue=False):
                try:
                    payload = json.loads(message.body)
                    await handler(payload)
                except Exception as e:
                    raise

        await self._queue.consume(on_message)
