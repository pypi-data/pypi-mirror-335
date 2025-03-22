import json

from redis import Redis
from redis.asyncio import Redis as ARedis


class RedisPubSub:
    def __init__(self, redis: Redis):
        self.redis = redis

    def publish(self, topic: str, value: str | dict) -> None:
        if isinstance(value, dict):
            value = json.dumps(value)

        self.redis.publish(topic, value)


class AsyncRedisPubSub:
    def __init__(self, redis: ARedis):
        self.redis = redis

    async def subscribe(self, topic, callback):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(topic)

        async for msg in pubsub.listen():
            if msg["type"] != "message":
                continue
            data = msg["data"]
            await callback(json.loads(data.decode("utf-8")))
