from abc import ABC, abstractmethod


class AbstractRabbitMQClient(ABC):

    @property
    @abstractmethod
    def port_api(self) -> int:
        raise NotImplementedError("Getter vhost is not implemented.")

    @property
    @abstractmethod
    def host(self) -> str:
        raise NotImplementedError("Getter host is not implemented.")

    @property
    @abstractmethod
    def port(self) -> int:
        raise NotImplementedError("Getter port is not implemented.")

    @property
    def username(self) -> str:
        raise NotImplementedError("Getter username is not implemented.")

    @property
    def password(self) -> str:
        raise NotImplementedError("Getter password is not implemented.")

    @property
    def uri(self) -> str:
        raise NotImplementedError("Getter vhost is not implemented.")
