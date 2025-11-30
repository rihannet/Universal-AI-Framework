from __future__ import annotations
from typing import Optional, Any, Dict, List
from .redis_memory import RedisMemory
from .vector_memory import VectorMemory
from .postgres_memory import PostgresMemory

class MemoryFacade:
    """
    Unified Memory API for Planner / LangGraph nodes
    Automatically initializes components if not provided
    """

    def __init__(self, redis: Optional[RedisMemory] = None,
                 vector: Optional[VectorMemory] = None,
                 structured: Optional[PostgresMemory] = None,
                 enable_vector: bool = False):
        self.redis = redis
        # Only initialize vector memory if explicitly enabled (requires Pinecone credentials)
        self.vector = vector if vector or not enable_vector else VectorMemory()
        self.structured = structured

    # Short-Term Memory
    def set_temp(self, key: str, value: Any, ttl: Optional[int] = None):
        if not self.redis:
            raise RuntimeError("RedisMemory not initialized")
        self.redis.set(key, value, ttl)

    def get_temp(self, key: str) -> Optional[str]:
        if not self.redis:
            raise RuntimeError("RedisMemory not initialized")
        return self.redis.get(key)

    # Long-Term Memory
    def store_vector(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        if not self.vector:
            raise RuntimeError("VectorMemory not initialized")
        self.vector.upsert(id, vector, metadata)

    def query_vector(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.vector:
            raise RuntimeError("VectorMemory not initialized")
        return self.vector.query(vector, top_k)

    # Structured Memory
    def insert_structured(self, table: str, data: Dict[str, Any]):
        if not self.structured:
            raise RuntimeError("PostgresMemory not initialized")
        self.structured.insert(table, data)

    def fetch_one_structured(self, table: str, where: str, params: Optional[List[Any]] = None):
        if not self.structured:
            raise RuntimeError("PostgresMemory not initialized")
        return self.structured.fetch_one(table, where, params)

    def fetch_all_structured(self, table: str, where: str = "TRUE", params: Optional[List[Any]] = None):
        if not self.structured:
            raise RuntimeError("PostgresMemory not initialized")
        return self.structured.fetch_all(table, where, params)
    
    # Simple store/retrieve API
    def store(self, key: str, data: Any) -> str:
        """Store data in Redis memory"""
        if self.redis:
            self.redis.set(key, str(data))
            return key
        return "memory_stored"
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from Redis memory"""
        if self.redis:
            return self.redis.get(key)
        return None
