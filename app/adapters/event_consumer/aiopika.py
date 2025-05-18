from app.ports.event_consumer import IEventConsumerPort
from typing import Callable, Awaitable
import aio_pika
import asyncio
import json


class AioPikaEventConsumerAdapter(IEventConsumerPort):
    def __init__(
        self,
        connection_url: str,
        exchange_name: str = "events",
        queue_name: str = "",
    ):
        self.connection_url = connection_url
        self.exchange_name = exchange_name
        self.queue_name = queue_name

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

        self._queue = await self._channel.declare_queue(
            self.queue_name or "",
            durable=True,
        )

    async def create_consuming_loop(
        self,
        routing_keys: list[str],
        handler: Callable[[dict], Awaitable[None]],
    ) -> asyncio.Task:
        for key in routing_keys:
            await self._queue.bind(self._exchange, routing_key=key)

        async def consume():
            async with self._queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            payload = json.loads(message.body)
                            await handler(payload)
                        except Exception as e:
                            print("Error during processing message: ", e)

        return asyncio.create_task(consume())
