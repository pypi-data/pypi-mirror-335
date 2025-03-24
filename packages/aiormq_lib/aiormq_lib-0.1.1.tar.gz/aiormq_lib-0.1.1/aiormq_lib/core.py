from .mixins.connection_mixin import ConnectionMixin
from .mixins.queue_mixin import QueueMixin
from .mixins.api_mixins import APIMixin
from .mixins.listener_mixin import ListenerMixin


class RabbitMQClient(ConnectionMixin, QueueMixin, APIMixin, ListenerMixin):
    def __init__(
        self, host: str, port: int, username: str, password: str, port_api: int = 15672
    ):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__port_api = port_api

    @property
    def port_api(self) -> int:
        return self.__port_api

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def username(self) -> str:
        return self.__username

    @property
    def password(self) -> str:
        return self.__password

    @property
    def uri(self):
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/"
