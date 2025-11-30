from __future__ import annotations
from typing import Optional, Dict, Any
from .redis_connector import RedisConnector


class StateManagerFacade:
    """
    Layer-1 State Manager main entrypoint.
    Plug-and-play Redis-based runtime state manager.
    """

    def __init__(self, redis_connector: Optional[RedisConnector] = None):
        self.redis = redis_connector or RedisConnector()

    # ---------------- Workflow State ----------------
    def set_workflow_state(self, workflow_id: str, state: str):
        self.redis.set_json(f"workflow:{workflow_id}:state", {"state": state})

    def get_workflow_state(self, workflow_id: str) -> Optional[str]:
        data = self.redis.get_json(f"workflow:{workflow_id}:state")
        return data.get("state") if data else None

    # ---------------- Task Assignment ----------------
    def assign_task(self, task_id: str, worker_id: str):
        self.redis.set_json(f"task:{task_id}:assigned_to", {"worker": worker_id})

    def get_task_assignment(self, task_id: str) -> Optional[str]:
        data = self.redis.get_json(f"task:{task_id}:assigned_to")
        return data.get("worker") if data else None

    # ---------------- Agent Status ----------------
    def set_agent_status(self, agent_id: str, status: str):
        self.redis.set_json(f"agent:{agent_id}:status", {"status": status})

    def get_agent_status(self, agent_id: str) -> Optional[str]:
        data = self.redis.get_json(f"agent:{agent_id}:status")
        return data.get("status") if data else None

    # ---------------- Checkpoints ----------------
    def set_checkpoint(self, key: str, checkpoint: Dict[str, Any], ttl: Optional[int] = None):
        self.redis.set_json(f"checkpoint:{key}", checkpoint, ttl)

    def get_checkpoint(self, key: str) -> Optional[Dict[str, Any]]:
        return self.redis.get_json(f"checkpoint:{key}")

    # ---------------- Pub/Sub ----------------
    def publish_event(self, channel: str, message: str):
        self.redis.publish(channel, message)
