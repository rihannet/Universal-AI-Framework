from __future__ import annotations
from typing import Dict, Any
from ..core.state import PlannerState
from ..core.graph import PlannerBindings
from ..core.errors import MissingBindingError


def intent_node(state: PlannerState, bindings: PlannerBindings) -> PlannerState:
    """
    Intent extraction node. Without an LLM binding this node will return inert status.
    When an LLM is bound, the LLM callable is expected to accept:
        llm(prompt: str, **kwargs) -> str
    and return a string or structured result the node can parse.
    """
    if bindings.llm is None:
        raise MissingBindingError("LLM binding not set for intent_node")

    prompt = (
        "Extract the intent, constraints, and important context from this user goal.\n\n"
        f"Goal: {state.goal}\n\n"
        "Return a short JSON with keys: intent, constraints, assumptions."
    )
    raw = bindings.llm(prompt)
    state.context.setdefault("intent_extraction", {})
    state.context["intent_extraction"]["raw"] = raw
    return state
