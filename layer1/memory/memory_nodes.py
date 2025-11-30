from __future__ import annotations
from typing import Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from planner.core.state import PlannerState
from planner.core.graph import PlannerBindings
from planner.core.errors import MissingBindingError

def memory_write_node(state: PlannerState, bindings: PlannerBindings) -> PlannerState:
    """
    Example memory write node for LangGraph
    Writes state.steps / context to MemoryFacade if registered
    """
    if not hasattr(bindings, "memory") or bindings.memory is None:
        raise MissingBindingError("MemoryFacade binding required for memory_write_node")

    memory_facade = bindings.memory
    # example: store current plan in Redis short-term
    memory_facade.set_temp(f"workflow:{state.workflow_id}", str(state.__dict__))
    return state

def memory_read_node(state: PlannerState, bindings: PlannerBindings) -> PlannerState:
    """
    Example memory read node for LangGraph
    Reads from MemoryFacade and updates state.context
    """
    if not hasattr(bindings, "memory") or bindings.memory is None:
        raise MissingBindingError("MemoryFacade binding required for memory_read_node")

    memory_facade = bindings.memory
    data = memory_facade.get_temp(f"workflow:{state.workflow_id}")
    if data:
        state.context["memory_snapshot"] = data
    return state
