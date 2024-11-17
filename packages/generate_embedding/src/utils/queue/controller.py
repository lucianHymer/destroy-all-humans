from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from ..hash import quickHash
from .helpers import print_error

if TYPE_CHECKING:
    from .message import Message
    from .types import QueueFactory
    from .queue import Queue


@dataclass
class QueueReceiveOptions:
    timeout: int = 0


class QueueListener:
    """Async context manager for listening to a queue"""

    def __init__(self, queue: "Queue", options: Optional[QueueReceiveOptions] = None):
        self.queue = queue
        self.options = options
        self._running = False
        self._current_message: Optional["Message"] = None

    async def __aenter__(self) -> "QueueListener":
        self._running = True
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        self._running = False
        if exc_type is not None:
            print_error(f"Error while listening to queue {self.queue.name}: {exc_val}")
        # If we have a current message and there was an error,
        # we might want to handle it here (e.g., put it back in the queue)
        self._current_message = None

    async def __aiter__(self) -> "QueueListener":
        return self

    async def __anext__(self) -> "Message":
        if not self._running:
            raise StopAsyncIteration

        self._current_message = await self.queue.receive(self.options)
        if self._current_message is None:
            # If we get None (timeout or no messages), stop iteration
            self._running = False
            raise StopAsyncIteration

        return self._current_message


class QueueController(ABC):
    """Abstract base class defining the interface for queue controllers"""

    def __init__(self, name: str, queue_factory: "QueueFactory"):
        self.queueId = quickHash(name)
        self.queue_factory = queue_factory

    @abstractmethod
    async def send(self, message: "Message") -> None:
        pass

    @abstractmethod
    async def receive(
        self, options: QueueReceiveOptions | None = None
    ) -> "Message | None":
        pass

    @abstractmethod
    async def count(self) -> int:
        pass
