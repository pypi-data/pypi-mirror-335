import json

from redis import Redis
from redis.asyncio import Redis as ARedis


class RedisQueue:
    def __init__(self, redis: Redis, queue: str, max_size: int | None = 5):
        self.redis = redis
        self.queue = queue
        self.max_size = max_size

    def push(self, value: str | dict) -> None:
        if isinstance(value, dict):
            value = json.dumps(value)

        pipe = self.redis.pipeline()
        pipe.lpush(self.queue, value)
        if self.max_size is not None:
            pipe.ltrim(self.queue, 0, self.max_size - 1)
        pipe.execute()

    def pop(self) -> dict | None:
        value = self.redis.brpop([self.queue])
        if value:
            return json.loads(value[1])

        return None

    def clear(self) -> None:
        self.redis.delete(self.queue)


class AsyncRedisQueue:
    def __init__(self, redis: ARedis, queue: str, max_size: int | None = 5):
        self.redis = redis
        self.queue = queue
        self.max_size = max_size

    async def push(self, value: str | dict):
        if isinstance(value, dict):
            value = json.dumps(value)

        pipe = self.redis.pipeline()
        pipe.lpush(self.queue, value)
        if self.max_size is not None:
            pipe.ltrim(self.queue, 0, self.max_size - 1)
        await pipe.execute()

    async def pop(self) -> dict | None:
        value = await self.redis.brpop([self.queue])
        if value:
            return json.loads(value[1])

        return None

    async def clear(self) -> None:
        await self.redis.delete(self.queue)
