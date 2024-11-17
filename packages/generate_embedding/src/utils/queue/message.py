from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from .types import JsonValue
from .serialization import serialize_json, deserialize_json

if TYPE_CHECKING:
    from .types import QueueFactory
    from .controller import QueueReceiveOptions
    from .queue import Queue


@dataclass
class Message:
    """Message container with response handling"""

    id: str
    timestamp: datetime
    queue_name: str
    data: JsonValue
    _queue_factory: "QueueFactory"

    @property
    def response_queue_name(self) -> str:
        return f"response:{self.id}"

    async def respond(self, data: JsonValue) -> "Message":
        response_queue = self.get_response_queue()
        return await response_queue.send(data)

    def get_response_queue(self) -> "Queue":
        """Get queue for responses to this message"""
        return self._queue_factory(self.response_queue_name)

    async def receive_response(
        self, options: "QueueReceiveOptions | None" = None
    ) -> "Message | None":
        """Wait for and receive response to this message"""
        response_queue = self.get_response_queue()
        return await response_queue.receive(options)

    def to_json(self) -> str:
        return serialize_json(
            {
                "id": self.id,
                "timestamp": self.timestamp,
                "queue_name": self.queue_name,
                "data": self.data,
            }
        )

    @classmethod
    def from_json(cls, json_str: str, queue_factory: "QueueFactory") -> "Message":
        data = deserialize_json(json_str)
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            queue_name=data["queue_name"],
            data=data["data"],
            _queue_factory=queue_factory,
        )
