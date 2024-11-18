from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any
from pydantic import BaseModel
import json
from .types import JsonValue

if TYPE_CHECKING:
    from .types import QueueFactory
    from .controller import QueueReceiveOptions
    from .queue import Queue


class MessageModel(BaseModel):
    id: str
    timestamp: datetime
    queue_name: str
    data: Any


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

    def get_response_queue(self) -> "Queue":
        """Get queue for responses to this message"""
        return self._queue_factory(self.response_queue_name)

    async def receive_response(
        self, options: "QueueReceiveOptions | None" = None
    ) -> "Message | None":
        """Wait for and receive response to this message"""
        response_queue = self.get_response_queue()
        return await response_queue.receive(options)

    async def respond(self, data: JsonValue) -> "Message":
        """Send a response to this message"""
        response_queue = self.get_response_queue()
        return await response_queue.send(data)

    def to_json(self) -> str:
        return MessageModel(
            id=self.id,
            timestamp=self.timestamp,
            queue_name=self.queue_name,
            data=self.data,
        ).model_dump_json()

    @classmethod
    def from_json(cls, json_str: str, queue_factory: "QueueFactory") -> "Message":
        message = MessageModel(**json.loads(json_str))
        return cls(
            id=message.id,
            timestamp=message.timestamp,
            queue_name=message.queue_name,
            data=message.data,
            _queue_factory=queue_factory,
        )
