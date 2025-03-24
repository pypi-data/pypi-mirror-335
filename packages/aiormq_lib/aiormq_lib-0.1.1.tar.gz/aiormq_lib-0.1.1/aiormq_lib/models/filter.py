from abc import abstractmethod

from .message import IncomingMessage


class BaseFilter:
    @abstractmethod
    async def __call__(self, message: IncomingMessage) -> bool:
        raise NotImplementedError("Method __call__ is not implemented.")
