from typing import Any, Callable

from .filter import BaseFilter


class QueueHandler:
    """QueueHandler is a class that represents a queue handler."""

    def __init__(
        self,
        func: Callable[..., Any],
        filters: list[BaseFilter],
    ):
        self.func = func
        self.filters = filters
