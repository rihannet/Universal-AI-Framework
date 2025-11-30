from __future__ import annotations
from typing import Any, List, Dict, Optional
import os
from pinecone import Pinecone, ServerlessSpec

class VectorMemory:
    """
    Long-Term Semantic Memory using Pinecone v3+
    Reads API key from environment variables for security
    """

    def __init__(self, index_name: str = "layer1-memory", dimension: int = 1536):
        # Read credentials from environment variables
        api_key = os.getenv("PINECONE_API_KEY")
        
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        # Initialize Pinecone v3+
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        
        # Create index if it doesn't exist
        existing = [idx["name"] for idx in self.pc.list_indexes()]
        if index_name not in existing:
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        
        self.index = self.pc.Index(index_name)

    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        self.index.upsert([(id, vector, metadata or {})])

    def query(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        result = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        return result.get("matches", [])

    def delete(self, id: str):
        self.index.delete(ids=[id])
