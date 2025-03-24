import json
from typing import Optional

from ..abc.connection import AbstractConnectionMixin
from ..models import Queue, Message
from ..exceptions import QueueCreateError, QueueSendError


class QueueMixin(AbstractConnectionMixin):

    async def create_queue(self, queue_name: str, durable: bool = True) -> Queue:
        """Creating a queue."""
        try:
            queue = await self.channel.declare_queue(queue_name, durable=durable)
            return queue  # type: ignore
        except Exception as e:
            raise QueueCreateError(e)

    async def send_message(
        self, queue_name: str, message: dict, headers: Optional[dict] = None
    ):
        """Send a message to a queue."""
        try:
            await self.channel.default_exchange.publish(
                Message(
                    headers=headers,
                    content_type="application/json",
                    body=json.dumps(message).encode(),
                ),
                routing_key=queue_name,
            )
        except Exception as e:
            raise QueueSendError(e)

    async def send_to_dlq(self, queue_name: str, message: Message):
        """Send a message to a single Dead Letter Queue (DLQ) with original queue info."""
        try:
            message.headers = message.headers or {}
            message.headers["original_queue"] = queue_name
            await self.channel.default_exchange.publish(message, routing_key="dlq")
        except Exception as e:
            raise QueueSendError(f"Failed to send message to DLQ: {e}")
