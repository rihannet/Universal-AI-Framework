from __future__ import annotations
from typing import Callable, Dict, Any, List, Optional
from ..core.state import PlannerState, Step
from ..core.errors import MissingBindingError, NodeExecutionError
import traceback


class PlannerBindings:
    """
    Container for external bindings. Planner remains inert if some bindings are not set.
    Each binding is optional; nodes should check availability.
    """
    def __init__(
        self,
        llm: Optional[Callable[..., Any]] = None,
        memory: Optional[Callable[..., Any]] = None,
        safety: Optional[Callable[..., Any]] = None,
        dispatch: Optional[Callable[..., Any]] = None,
    ):
        self.llm = llm
        self.memory = memory
        self.safety = safety
        self.dispatch = dispatch


class SimpleGraphPlanner:
    """
    A simple, deterministic graph-based planner engine.
    Nodes are executed in sequence defined by self._nodes list.
    """

    def __init__(self):
        self._nodes: List[Callable[[PlannerState, PlannerBindings], PlannerState]] = []
        self.bindings = PlannerBindings()

    def register_node(self, node_fn: Callable[[PlannerState, PlannerBindings], PlannerState]) -> None:
        self._nodes.append(node_fn)

    def bind_llm(self, llm_fn: Callable[..., Any]) -> None:
        self.bindings.llm = llm_fn

    def bind_memory(self, mem_fn: Callable[..., Any]) -> None:
        self.bindings.memory = mem_fn

    def bind_safety(self, safety_fn: Callable[..., Any]) -> None:
        self.bindings.safety = safety_fn

    def bind_dispatch(self, dispatch_fn: Callable[..., Any]) -> None:
        self.bindings.dispatch = dispatch_fn

    def run_full_plan(self, state: PlannerState) -> PlannerState:
        """
        Execute planner nodes in order. If a required binding is missing, the planner
        sets state.status = 'AWAITING_BINDINGS' and returns safely (inert).
        Nodes should themselves check bindings if they need them.
        """
        try:
            state.touch()
            if not self._nodes:
                state.status = "PLANNED"
                state.touch()
                return state

            for node in self._nodes:
                try:
                    state = node(state, self.bindings)
                    state.touch()
                except MissingBindingError:
                    state.status = "AWAITING_BINDINGS"
                    state.touch()
                    return state
                except Exception as e:
                    state.status = "ERROR"
                    state.touch()
                    raise NodeExecutionError(f"Node {node.__name__} failed: {e}") from e

            if state.status not in ("IN_PROGRESS", "DONE", "ERROR"):
                state.status = "PLANNED"
            state.touch()
            return state
        except Exception:
            raise
