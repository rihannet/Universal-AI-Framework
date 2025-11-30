from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time
import uuid


@dataclass
class Step:
    id: str
    title: str
    description: str
    requires_approval: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    routing: Dict[str, Any] = field(default_factory=dict)
    safety: Dict[str, Any] = field(default_factory=dict)
    results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PlannerState:
    workflow_id: str
    user_id: str
    goal: str
    context: Dict[str, Any]
    steps: List[Step] = field(default_factory=list)
    plan: List[Step] = field(default_factory=list)
    current_index: Optional[int] = 0
    selected_worker: Optional[str] = None
    reflection: Optional[Dict[str, Any]] = None
    status: str = "INITIAL"  # INITIAL, PLANNED, AWAITING_BINDINGS, IN_PROGRESS, DONE, ERROR
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @classmethod
    def new(cls, user_id: str, goal: str, context: Optional[Dict[str, Any]] = None) -> "PlannerState":
        return cls(
            workflow_id=f"wf_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            goal=goal,
            context=context or {},
            steps=[],
            current_index=None,
            status="INITIAL",
        )

    def touch(self):
        self.updated_at = time.time()
