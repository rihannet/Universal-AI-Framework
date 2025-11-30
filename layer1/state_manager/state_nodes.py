from __future__ import annotations
from typing import Any, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from planner.core.state import PlannerState
from .state_facade import StateManagerFacade


def save_workflow_state_node(state: PlannerState, facade: StateManagerFacade) -> PlannerState:
    """
    Node that writes the current workflow status to Redis.
    """
    if not state.workflow_id or not state.status:
        return state
    facade.set_workflow_state(state.workflow_id, state.status)
    return state


def save_task_assignment_node(state: PlannerState, task_id: str, worker_id: str, facade: StateManagerFacade) -> PlannerState:
    """
    Node that assigns a task to a worker in Redis.
    """
    facade.assign_task(task_id, worker_id)
    return state


def save_checkpoint_node(state: PlannerState, key: str, checkpoint: Dict[str, Any], facade: StateManagerFacade) -> PlannerState:
    """
    Node that saves checkpoints for steps/tasks.
    """
    facade.set_checkpoint(key, checkpoint)
    return state
