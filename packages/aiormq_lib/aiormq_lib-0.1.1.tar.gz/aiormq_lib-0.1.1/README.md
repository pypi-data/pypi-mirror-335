# rabbitmq

### Install

```bash
pip install aiormq_lib
```

### Example

```python
import asyncio

from aiormq_lib import RabbitMQClient
from aiormq_lib.models import BaseFilter
from aiormq_lib.models import IncomingMessage, Queue

# Create RabbitMQ client
client = RabbitMQClient(
    host="localhost",
    port=5672,
    username="username",
    password="password",
    port_api=15672,
)


# Filter for listener
class Filter(BaseFilter):
    async def __call__(self, message: IncomingMessage):
        # Not handling this message
        return False


# Add listener for queue "test_queue"
@client.listener("test_queue", Filter())
async def handle_message_1(queue: Queue, message: IncomingMessage):
    print(f"Received message: {message.body.decode()}")


async def handle_message_2(queue: Queue, message: IncomingMessage):
    print(f"Received message: {message.body.decode()}")


async def main():

    # If start_listening is True, start listening
    await client.connect(start_listening=True)

    # Add listener for queue "test_queue"
    await client.add_listener("test_queue", handle_message_2)

    await client.send_message("test_queue", {"content": "test"})  # Handler 2
    await asyncio.sleep(10)

    # Disconnect and stop listening
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
```
