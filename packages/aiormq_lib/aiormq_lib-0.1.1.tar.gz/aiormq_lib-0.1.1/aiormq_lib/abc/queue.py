from abc import ABC, abstractmethod

from ..models import Queue


class AbstractQueueMixin(ABC):
    @abstractmethod
    async def create_queue(self, queue_name: str) -> Queue:
        """Method for creating a queue."""
        raise NotImplementedError("Method create_queue is not implemented.")

    @abstractmethod
    async def send_message(self, queue_name: str, message: dict):
        """Method for sending messages to a queue."""
        raise NotImplementedError("Method send_message is not implemented.")

    @abstractmethod
    async def send_to_dlq(self, queue_name: str, message):
        """Method for sending messages to a Dead Letter Queue."""
        raise NotImplementedError("Method send_to_dlq is not implemented.")
