from abc import abstractmethod


class AbstractAPI:
    @property
    @abstractmethod
    def url_api(self):
        raise NotImplementedError("Getter url_api is not implemented.")

    @abstractmethod
    async def fetch_queues(self) -> list[str]:
        raise NotImplementedError("Method fetch_queues is not implemented.")
