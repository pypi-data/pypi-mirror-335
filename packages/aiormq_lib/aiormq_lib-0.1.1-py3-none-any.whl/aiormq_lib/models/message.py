from aio_pika import Message as MessageAIPika
from aio_pika.abc import AbstractIncomingMessage


class Message(MessageAIPika):
    pass


class IncomingMessage(AbstractIncomingMessage):
    pass
