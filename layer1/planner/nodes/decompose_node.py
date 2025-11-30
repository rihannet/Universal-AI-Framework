from __future__ import annotations
from typing import Dict, Any, List
from ..core.state import PlannerState, Step
from ..core.graph import PlannerBindings
from ..core.errors import MissingBindingError


def decompose_node(state: PlannerState, bindings: PlannerBindings) -> PlannerState:
    """
    Decomposition node. Must use LLM to produce steps.
    Contract:
      - bindings.llm(prompt) -> str (ideally JSON or newline list)
      - nodes must create Step objects in state.steps

    If no LLM: raise MissingBindingError to indicate inert planner.
    """
    if bindings.llm is None:
        raise MissingBindingError("LLM binding not set for decompose_node")

    intent_info = state.context.get("intent_extraction", {}).get("raw", "")
    prompt = (
        "Break down the goal into a focused ordered list of steps. Each step should be "
        "an atomic action with a short title and short description.\n\n"
        f"Goal: {state.goal}\n\n"
        f"Context / intent: {intent_info}\n\n"
        "Return steps as a numbered list or JSON."
    )

    raw = bindings.llm(prompt)
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    steps: List[Step] = []
    idx = 1
    for line in lines:
        text = line
        for sep in (".", ")", "-"):
            if text.startswith(f"{idx}{sep}") or text.startswith(f"{idx}{sep} "):
                text = text.split(sep, 1)[1].strip()
                break
        if ":" in text:
            title, description = [p.strip() for p in text.split(":", 1)]
        elif " - " in text:
            title, description = [p.strip() for p in text.split(" - ", 1)]
        else:
            parts = text.split(" ", 4)
            title = " ".join(parts[:3]).strip()
            description = text
        step = Step(id=f"step_{idx}", title=title[:64], description=description[:512], requires_approval=True)
        steps.append(step)
        idx += 1

    state.steps = steps
    state.current_index = 0 if steps else None
    return state
