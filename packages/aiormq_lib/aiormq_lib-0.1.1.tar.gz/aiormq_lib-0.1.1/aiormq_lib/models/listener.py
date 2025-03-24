from asyncio import Task

from .queue_handler import QueueHandler


class Listener:
    __task: Task

    def __init__(self, queue_name: str, handler: QueueHandler):
        self.queue_name = queue_name
        self.handlers = [handler]

    @property
    def task(self) -> Task:
        return self.__task

    @task.setter
    def task(self, task: Task):
        self.__task = task
