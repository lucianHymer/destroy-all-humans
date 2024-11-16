from .hash import quickHash
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
import redis.asyncio as redis
from typing import Optional, Any, TypeAlias, Type
import json
import uuid
import sys


def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class QueueError(Exception):
    """Base class for Queue exceptions"""

    pass


class QueueConnectionError(QueueError):
    """Raised when there's an error connecting to the queue backend"""

    pass


class QueueSerializationError(QueueError):
    """Raised when there's an error serializing/deserializing queue data"""

    pass


JsonValue: TypeAlias = (
    str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)


def json_serializer_default(obj: Any) -> JsonValue:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    try:
        # Try to convert to dict for dataclasses or objects with __dict__
        return obj.__dict__
    except AttributeError:
        pass
    try:
        # Try to convert to list for iterables
        return list(obj)
    except TypeError:
        pass
    raise QueueSerializationError(
        f"Object of type {type(obj)} is not JSON-serializable"
    )


def json_deserializer_object_hook(obj: dict) -> Any:
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                # Try to parse as ISO date
                obj[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return obj


def serialize_json(obj: Any) -> str:
    """Serialize object to JSON string with custom encoding"""
    try:
        return json.dumps(obj, default=json_serializer_default)
    except TypeError as e:
        raise QueueSerializationError(f"Failed to serialize object: {str(e)}")


def deserialize_json(json_str: str) -> Any:
    """Deserialize JSON string with custom decoding"""
    try:
        return json.loads(json_str, object_hook=json_deserializer_object_hook)
    except json.JSONDecodeError as e:
        raise QueueSerializationError(f"Failed to deserialize JSON: {str(e)}")


class QueueUnexpectedError(QueueError):
    """Raised when an unexpected error occurs"""

    pass


@dataclass
class QueueReceiveOptions:
    timeout: int = 0


@dataclass
class Message:
    """Message container with response handling"""

    id: str
    timestamp: datetime
    queue_name: str
    data: JsonValue
    _controllerType: Type["QueueController"]

    @property
    def response_queue_name(self) -> str:
        return f"response:{self.id}"

    async def respond(self, data: JsonValue) -> "Message":
        response_queue = self.get_response_queue()
        return await response_queue.send(data)

    def get_response_queue(self) -> "Queue":
        """Get queue for responses to this message"""
        return Queue(self.response_queue_name, self._controllerType)

    async def receive_response(self, options: Optional[QueueReceiveOptions] = None):
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
    def from_json(
        cls, json_str: str, controllerType: Type["QueueController"]
    ) -> "Message":
        data = deserialize_json(json_str)
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            queue_name=data["queue_name"],
            data=data["data"],
            _controllerType=controllerType,
        )


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
        # If we have a current message and there was an error,
        # we might want to handle it here (e.g., put it back in the queue)
        self._current_message = None

    async def __aiter__(self) -> "QueueListener":
        return self

    async def __anext__(self) -> Message:
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

    def __init__(self, name: str):
        self.queueId = quickHash(name)

    @abstractmethod
    async def send(self, message: Message) -> None:
        pass

    @abstractmethod
    async def receive(
        self, options: Optional[QueueReceiveOptions] = None
    ) -> Optional[Message]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass


class RedisQueueController(QueueController):
    """Redis implementation of QueueController"""

    def __init__(self, name: str, redis_client=None):
        super().__init__(name)
        self.queue_key = f"queue:{self.queueId}"
        self.redis = redis_client or redis.Redis(
            host="localhost", port=6379, decode_responses=True
        )

    async def send(self, message: Message) -> None:
        """Send a message to the queue"""
        try:
            await self.redis.lpush(self.queue_key, message.to_json())
        except redis.RedisError as e:
            raise QueueConnectionError(f"Failed to send message: {str(e)}")
        except (TypeError, ValueError) as e:
            raise QueueSerializationError(f"Failed to serialize message: {str(e)}")

    async def receive(
        self, options: Optional[QueueReceiveOptions] = None
    ) -> Optional[Message]:
        """Receive next message from queue"""
        try:
            timeout = options.timeout if options else 0
            result = await self.redis.brpop(self.queue_key, timeout=timeout)
            if not result:
                return None

            return Message.from_json(result[1], RedisQueueController)
        except redis.RedisError as e:
            raise QueueConnectionError(f"Failed to receive message: {str(e)}")
        except json.JSONDecodeError as e:
            raise QueueSerializationError(f"Failed to parse message: {str(e)}")

    async def count(self) -> int:
        """Get number of messages in queue"""
        try:
            return await self.redis.llen(self.queue_key)
        except redis.RedisError as e:
            raise QueueConnectionError(f"Failed to get queue count: {str(e)}")


class Queue:
    """App interface for working with a queue"""

    def __init__(
        self, name: str, controllerType: type[QueueController] = RedisQueueController
    ):
        self.name = name
        self._controller: QueueController = controllerType(name)

    async def send(self, data: JsonValue) -> Message:
        """Send data and return a Message object"""
        print_error(
            f"Sending message to queue {self.name} of type {type(self._controller)}"
        )
        message = Message(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            queue_name=self.name,
            data=data,
            _controllerType=type(self._controller),
        )
        await self._controller.send(message)
        return message

    async def receive(
        self, options: Optional[QueueReceiveOptions] = None
    ) -> Optional[Message]:
        """Receive next message from queue"""
        return await self._controller.receive(options)

    async def count(self) -> int:
        return await self._controller.count()

    async def query(
        self, data: JsonValue, options: Optional[QueueReceiveOptions] = None
    ) -> Optional[Message]:
        message = await self.send(data)
        return await message.receive_response(options)

    def listen(self, options: Optional[QueueReceiveOptions] = None) -> "QueueListener":
        """Create a context manager for listening to the queue"""
        return QueueListener(self, options)


print_error("queue.py loaded")
