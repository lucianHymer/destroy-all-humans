from ..controller import QueueController, QueueReceiveOptions
from ..types import QueueFactory
from ..message import Message
from ..errors import QueueConnectionError, QueueSerializationError

import redis.asyncio as redis
import json


class RedisQueueController(QueueController):
    """Redis implementation of QueueController"""

    _pool = None

    @classmethod
    def create_pool(cls, host="localhost", port=6379, max_connections=10, **kwargs):
        """Initialize Redis connection pool"""
        if cls._pool is None:
            pool = redis.ConnectionPool(
                host=host,
                port=port,
                max_connections=max_connections,
                decode_responses=True,
                **kwargs,
            )
            cls._pool = pool
        return cls._pool

    def __init__(self, name: str, queue_factory: QueueFactory):
        super().__init__(name, queue_factory)
        self.queue_key = f"queue:{self.queueId}"
        if self._pool is None:
            self._pool = self.create_pool()
        self.redis = redis.Redis(connection_pool=self._pool, decode_responses=True)

    async def send(self, message: "Message") -> None:
        """Send a message to the queue"""
        try:
            await self.redis.lpush(self.queue_key, message.to_json())
        except redis.RedisError as e:
            raise QueueConnectionError(f"Failed to send message: {str(e)}")
        except (TypeError, ValueError) as e:
            raise QueueSerializationError(f"Failed to serialize message: {str(e)}")

    async def receive(
        self, options: QueueReceiveOptions | None = None
    ) -> "Message | None":
        """Receive next message from queue"""
        try:
            timeout = options.timeout if options else 0
            result = await self.redis.brpop(self.queue_key, timeout=timeout)
            if not result:
                return None

            return Message.from_json(result[1], self.queue_factory)
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

    @classmethod
    async def cleanup(cls):
        """Cleanup connection pool - call during application shutdown"""
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None
