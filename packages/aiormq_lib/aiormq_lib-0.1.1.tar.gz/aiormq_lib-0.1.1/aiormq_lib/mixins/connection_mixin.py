from aio_pika import connect_robust

from ..abc.client import AbstractRabbitMQClient
from ..abc.listener import AbstractListenerMixin
from ..models import Connection, Channel


class ConnectionMixin(AbstractRabbitMQClient, AbstractListenerMixin):
    __connection: Connection
    __channel: Channel

    @property
    def connection(self) -> Connection:
        return self.__connection

    @connection.setter
    def connection(self, value: Connection):
        self.__connection = value

    @property
    def channel(self) -> Channel:
        return self.__channel

    @channel.setter
    def channel(self, value: Channel):
        self.__channel = value

    async def connect(self, start_listening: bool = False):
        """Connect to RabbitMQ and create channel. If start_listening is True, start listening."""
        self.connection = await connect_robust(url=self.uri)  # type: ignore
        self.channel = await self.connection.channel()  # type: ignore

        if start_listening:
            await self.start_listening()

    async def disconnect(self):
        """Close channel and connection and stop listening."""

        await self.stop_listening()

        if not self.channel.is_closed:
            await self.channel.close()
        if not self.connection.is_closed:
            await self.connection.close()
