from aiohttp import ClientSession, BasicAuth

from ..abc.client import AbstractRabbitMQClient
from ..abc.api import AbstractAPI
from ..abc.connection import AbstractConnectionMixin
from ..exceptions import APIFetchQueuesError


class APIMixin(AbstractRabbitMQClient, AbstractAPI, AbstractConnectionMixin):

    @property
    def url_api(self) -> str:
        return f"http://{self.host}:{str(self.port_api)}/api"

    async def fetch_queues(self) -> list[str]:
        """Fetches queues from RabbitMQ API.

        Returns:
            list[str]: List of queues names
        """
        try:
            async with ClientSession() as session:
                async with session.get(
                    self.url_api + "/queues",
                    auth=BasicAuth(self.username, self.password),
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Failed to fetch queues: status code is {response.status}."
                        )
                    else:
                        queues = []
                        for queue in await response.json():
                            queues.append(queue["name"])
                        return queues
        except Exception as e:
            raise APIFetchQueuesError(e)
