from typing import Optional, TYPE_CHECKING
from .queue import QueueReceiveOptions
from .helpers import print_error

if TYPE_CHECKING:
    from .queue import Queue


class QueueListener:
    """Queue listener that provides async iteration over messages"""

    def __init__(self, queue: "Queue", options: Optional[QueueReceiveOptions] = None):
        self.queue = queue
        self.options = options

    def __aiter__(self):
        """Make the QueueListener directly iterable"""
        return self

    async def __anext__(self):
        """Get next message from the queue"""
        try:
            message = await self.queue.receive(self.options)
            if message is None:
                raise StopAsyncIteration
            return message
        except Exception as e:
            print_error(f"Error while listening to queue {self.queue.name}: {e}")
            raise StopAsyncIteration
