from __future__ import annotations
from typing import Callable, Optional, Dict, Any
from ..core.state import PlannerState


class Router:
    """
    The Router is responsible for selecting a worker for a given step.
    This Router is intentionally minimal and *does not* call external systems.
    Instead it exposes `select_worker` and allows an external function to be registered
    later (by planner_main.register_worker_selector).

    If no selector is registered, Router.select_worker will mark the state as
    waiting for bindings (safe, inert).
    """

    def __init__(self):
        self._worker_selector: Optional[Callable[[PlannerState, Dict[str, Any]], str]] = None

    def register_selector(self, selector: Callable[[PlannerState, Dict[str, Any]], str]) -> None:
        """
        Register an external worker selection function.
        Signature: selector(state, step_dict) -> worker_name (str)
        """
        self._worker_selector = selector

    def select_worker(self, state: PlannerState, step: Dict[str, Any]) -> Optional[str]:
        """
        Return the selected worker name or None if no binding exists.
        Does not perform dispatch.
        """
        if self._worker_selector is None:
            return None
        return self._worker_selector(state, step)
