from __future__ import annotations
import redis
from typing import Any, Optional

class RedisMemory:
    """
    Short-Term Memory using Redis (in-memory, fast, TTL supported)
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 3600):
        self.ttl = ttl
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        self.redis_client.set(key, value, ex=ttl or self.ttl)

    def get(self, key: str) -> Optional[str]:
        return self.redis_client.get(key)

    def delete(self, key: str):
        self.redis_client.delete(key)

    def exists(self, key: str) -> bool:
        return self.redis_client.exists(key) > 0
