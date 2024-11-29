from typing import Type
from datetime import datetime, timezone
import uuid
from .message import Message
from .controller import QueueController, QueueReceiveOptions
from .controllers.redis_queue_controller import RedisQueueController
from .helpers import print_error
from .listener import QueueListener


class Queue:
    """App interface for working with a queue"""

    def __init__(
        self, name: str, controller_class: Type[QueueController] = RedisQueueController
    ):
        self.name = name
        self._controller = controller_class(name, self._create_queue)

    def _create_queue(self, name: str) -> "Queue":
        """Factory function for creating new queues with same controller type"""
        return Queue(name, type(self._controller))

    async def send(self, serialized_data: bytes) -> Message:
        """Send data and return a Message object"""
        print_error(
            f"Sending message to queue {self.name} of type {type(self._controller)}"
        )
        message = Message(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            queue_name=self.name,
            serialized_data=serialized_data,
            _queue_factory=self._create_queue,
        )
        await self._controller.send(message)
        return message

    async def receive(
        self, options: QueueReceiveOptions | None = None
    ) -> Message | None:
        """Receive next message from queue"""
        return await self._controller.receive(options)

    async def count(self) -> int:
        return await self._controller.count()

    async def query(
        self, serialized_data: bytes, options: QueueReceiveOptions | None = None
    ) -> Message | None:
        message = await self.send(serialized_data)
        return await message.receive_response(options)

    # Example:
    # async with queue.listen() as listener:
    #     async for message in listener:
    #         print(f"Received message")
    def listen(self, options: QueueReceiveOptions | None = None) -> QueueListener:
        """Create a context manager for listening to the queue"""
        return QueueListener(self, options)

    @classmethod
    async def cleanup(cls):
        """Cleanup any resources used by the queue"""
        await RedisQueueController.cleanup()
