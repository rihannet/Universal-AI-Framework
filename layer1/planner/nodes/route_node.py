from __future__ import annotations
from typing import Dict, Any, Optional
from ..core.state import PlannerState
from ..core.graph import PlannerBindings
from ..core.errors import MissingBindingError


def route_node(state: PlannerState, bindings: PlannerBindings) -> PlannerState:
    """
    Routing node: chooses worker for the plan. If an external Router/worker selector is bound
    (planner_main will register it via graph.bindings.dispatch or via planner_main.register_worker_selector),
    this function will call it. Otherwise it will raise MissingBindingError to indicate inert planner.
    """

    if bindings.dispatch is None:
        raise MissingBindingError("Dispatch/worker selector binding not set for route_node")

    if state.current_index is None:
        return state

    step = state.steps[state.current_index]
    step_dict = {"id": step.id, "title": step.title, "description": step.description}
    worker = bindings.dispatch(state, step_dict)
    state.selected_worker = worker
    step.routing["worker"] = worker
    return state
