from __future__ import annotations
from ..core.state import PlannerState
from ..core.graph import PlannerBindings


def finalize_node(state: PlannerState, bindings: PlannerBindings) -> PlannerState:
    """
    Finalization node. Prepares plan state for external consumption.
    Does not call any external services; it's purely structural.
    """
    state.plan = state.steps
    state.status = "PLANNED"
    if state.current_index is None and state.steps:
        state.current_index = 0
    return state
