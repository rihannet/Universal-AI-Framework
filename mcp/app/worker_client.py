# app/worker_client.py
import os
import asyncio
import redis.asyncio as redis
import json
from typing import Dict

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

class RedisClient:
    _conn = None

    @classmethod
    async def get(cls):
        if cls._conn is None:
            cls._conn = redis.from_url(REDIS_URL, decode_responses=True)
        return cls._conn

async def publish_task(task: Dict):
    r = await RedisClient.get()
    channel = "tasks_channel"
    await r.publish(channel, json.dumps(task))