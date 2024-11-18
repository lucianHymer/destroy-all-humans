from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from pydantic import BaseModel
from ..hash import quickHash

if TYPE_CHECKING:
    from .message import Message
    from .types import QueueFactory


@dataclass
class QueueReceiveOptions:
    timeout: int = 0
    override_data_model: BaseModel | None = None


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
