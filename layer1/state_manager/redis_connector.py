from typing import Any, Dict, Optional
import redis
import json


class RedisConnector:
    """
    Raw Redis connection wrapper.
    Handles JSON serialization/deserialization and TTL.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, decode_responses: bool = True):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)

    def set_json(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        serialized = json.dumps(value)
        if ttl:
            self.client.setex(key, ttl, serialized)
        else:
            self.client.set(key, serialized)

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        val = self.client.get(key)
        if val is None:
            return None
        return json.loads(val)

    def delete(self, key: str):
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        return self.client.exists(key) == 1

    def publish(self, channel: str, message: str):
        self.client.publish(channel, message)
