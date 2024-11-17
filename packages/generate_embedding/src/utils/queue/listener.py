from typing import Optional, TYPE_CHECKING
from .message import Message
from .queue import QueueReceiveOptions
from .helpers import print_error

if TYPE_CHECKING:
    from .queue import Queue


class QueueListener:
    """Async context manager for listening to a queue"""

    def __init__(self, queue: "Queue", options: Optional[QueueReceiveOptions] = None):
        self.queue = queue
        self.options = options
        self._running = False
        self._current_message: Optional[Message] = None

    async def __aenter__(self) -> "QueueListener":
        self._running = True
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        self._running = False
        if exc_type is not None:
            print_error(f"Error while listening to queue {self.queue.name}: {exc_val}")
        self._current_message = None

    async def __aiter__(self) -> "QueueListener":
        return self

    async def __anext__(self) -> Message:
        if not self._running:
            raise StopAsyncIteration

        self._current_message = await self.queue.receive(self.options)
        if self._current_message is None:
            self._running = False
            raise StopAsyncIteration

        return self._current_message
