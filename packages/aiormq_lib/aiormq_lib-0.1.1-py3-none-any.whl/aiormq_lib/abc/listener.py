from abc import ABC, abstractmethod
from typing import Any, Callable

from ..models import Listener, BaseFilter


class AbstractListenerMixin(ABC):

    @property
    @abstractmethod
    def listeners(self) -> list[Listener]:
        raise NotImplementedError("Not implemented listeners.")

    @abstractmethod
    def start_listening(self):
        raise NotImplementedError("Not implemented start_listening.")

    @abstractmethod
    async def stop_listening(self):
        raise NotImplementedError("Not implemented stop_listening.")

    @abstractmethod
    def listener(self, queue_name: str, *filters: BaseFilter):
        raise NotImplementedError("Not implemented listener.")

    @abstractmethod
    async def add_listener(
        self, queue_name: str, func: Callable[..., Any], *filters: BaseFilter
    ):
        raise NotImplementedError("Not implemented add_listener.")

    @abstractmethod
    async def remove_listener(self, queue_name: str):
        raise NotImplementedError("Not implemented remove_listener.")
