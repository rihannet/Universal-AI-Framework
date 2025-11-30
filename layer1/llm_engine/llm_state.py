from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
import time
import uuid


@dataclass
class LLMCallState:
    call_id: str
    prompt: str
    response: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

    @classmethod
    def new(cls, prompt: str, metadata: Dict[str, Any] = None) -> "LLMCallState":
        return cls(
            call_id=f"llm_{uuid.uuid4().hex[:12]}",
            prompt=prompt,
            metadata=metadata or {},
        )

    def mark_completed(self, response: str):
        self.response = response
        self.completed_at = time.time()
