from __future__ import annotations
from typing import Callable, Optional, Dict, Any
from .core.graph import SimpleGraphPlanner, PlannerBindings
from .core.state import PlannerState
from .nodes.intent_node import intent_node
from .nodes.decompose_node import decompose_node
from .nodes.reflect_node import reflect_node
from .nodes.route_node import route_node
from .nodes.finalize_node import finalize_node
from .core.router import Router
from .core.errors import MissingBindingError


class Layer1Planner:
    """
    The entry point for the Layer-1 planner.

    Usage pattern:
      planner = Layer1Planner()
      planner.register_llm(my_llm_callable)
      planner.register_memory(my_memory_callable)
      planner.register_dispatch(my_worker_selector)
      planner.register_safety(my_safety_callable)

      state = planner.create_workflow(user_id="alice", goal="Deploy backend", context={})
      state = planner.plan_workflow(state)
    """

    def __init__(self):
        self._engine = SimpleGraphPlanner()
        self._router = Router()
        self._engine.register_node(intent_node)
        self._engine.register_node(decompose_node)
        self._engine.register_node(reflect_node)
        self._engine.register_node(route_node)
        self._engine.register_node(finalize_node)

    def register_llm(self, llm_callable: Callable[[str], str]) -> None:
        """Register an LLM callable: llm(prompt)->str"""
        self._engine.bind_llm(llm_callable)

    def register_memory(self, memory_callable: Callable[..., Any]) -> None:
        """Register a memory callable; not used by base planner nodes yet, available for future use."""
        self._engine.bind_memory(memory_callable)

    def register_safety(self, safety_callable: Callable[..., Any]) -> None:
        """Register a safety callable for future integration."""
        self._engine.bind_safety(safety_callable)

    def register_dispatch(self, worker_selector: Callable[[PlannerState, Dict[str, Any]], str]) -> None:
        """
        Register a worker selector / dispatch callable.
        This will be bound into the planner's dispatch binding and also into router helper.
        """
        self._engine.bind_dispatch(worker_selector)
        self._router.register_selector(worker_selector)

    def create_workflow(self, user_id: str, goal: str, context: Optional[Dict[str, Any]] = None) -> PlannerState:
        """
        Create an initial PlannerState; does not run nodes.
        """
        st = PlannerState.new(user_id=user_id, goal=goal, context=context or {})
        st.status = "CREATED"
        return st

    def plan_workflow(self, state: PlannerState) -> PlannerState:
        """
        Execute the full planner pipeline (all nodes).
        If required bindings are missing (LLM, dispatch, etc.), planner will return state.status == 'AWAITING_BINDINGS'
        and will not produce a real plan.
        """
        try:
            return self._engine.run_full_plan(state)
        except MissingBindingError:
            state.status = "AWAITING_BINDINGS"
            return state

    def step_workflow(self, state: PlannerState) -> PlannerState:
        """
        Run nodes incrementally (alias to plan_workflow for now).
        Provided for future granularity (run node-by-node).
        """
        return self.plan_workflow(state)

    def get_router(self) -> Router:
        return self._router
    
    def create_worker_blueprint(self, task: str) -> Dict[str, Any]:
        """Create worker blueprint from task analysis"""
        task_lower = task.lower()
        if any(kw in task_lower for kw in ['news', 'article', 'headlines']):
            return {"worker_name": "NewsWorker", "description": "Fetches news", "capabilities": ["news", "fetch", "articles"], "apis": {}}
        elif any(kw in task_lower for kw in ['research', 'search', 'find']):
            return {"worker_name": "ResearchWorker", "description": "Research information", "capabilities": ["research", "search", "find"], "apis": {}}
        elif any(kw in task_lower for kw in ['code', 'debug', 'fix', 'python']):
            return {"worker_name": "CodingWorker", "description": "Code debugging", "capabilities": ["code", "debug", "fix"], "apis": {}}
        elif any(kw in task_lower for kw in ['iot', 'home', 'lights', 'temperature']):
            return {"worker_name": "IoTWorker", "description": "IoT control", "capabilities": ["iot", "home", "lights"], "apis": {}}
        else:
            return {"worker_name": "echo", "description": "Default", "capabilities": [], "apis": {}}
