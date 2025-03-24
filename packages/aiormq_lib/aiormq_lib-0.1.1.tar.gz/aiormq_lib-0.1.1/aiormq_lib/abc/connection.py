from abc import ABC, abstractmethod

from ..models import Connection, Channel


class AbstractConnectionMixin(ABC):
    @property
    @abstractmethod
    def connection(self) -> Connection:
        """Получаем подключение с проверкой, что оно установлено."""
        raise NotImplementedError("Getter connection is not implemented.")

    @connection.setter
    @abstractmethod
    def connection(self, value: Connection):
        """Устанавливаем подключение."""
        raise NotImplementedError("Setter connection is not implemented.")

    @property
    @abstractmethod
    def channel(self) -> Channel:
        """Получаем канал с проверкой, что он открыт."""
        raise NotImplementedError("Getter channel is not implemented.")

    @channel.setter
    @abstractmethod
    def channel(self, value: Channel):
        """Устанавливаем канал."""
        raise NotImplementedError("Setter channel is not implemented.")

    @abstractmethod
    async def connect(self):
        """Подключаемся к брокеру RabbitMQ, используя Singleton и создаем канал."""
        raise NotImplementedError("Method connect is not implemented.")

    @abstractmethod
    async def disconnect(self):
        """Закрываем соединение."""
        raise NotImplementedError("Method disconnect is not implemented.")
