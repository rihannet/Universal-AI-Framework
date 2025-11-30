from __future__ import annotations
from typing import Dict, Any
from ..core.state import PlannerState
from ..core.graph import PlannerBindings
from ..core.errors import MissingBindingError


def reflect_node(state: PlannerState, bindings: PlannerBindings) -> PlannerState:
    """
    Reflection node. If safety or memory bindings are present, they may be used.
    If no LLM present, this node indicates that bindings are required to proceed.
    """
    if bindings.llm is None:
        raise MissingBindingError("LLM binding not set for reflect_node")

    plan_text = "\n".join([f"{s.id}. {s.title} - {s.description}" for s in state.steps])

    prompt = (
        "You are the reflection module. Evaluate the plan below for completeness, safety issues, "
        "missing steps, or ordering problems. If changes are needed, return an improved numbered list; "
        "otherwise return 'OK'.\n\n"
        f"Plan:\n{plan_text}\n"
    )
    raw = bindings.llm(prompt)
    if raw.strip().upper() == "OK":
        state.reflection = {"status": "OK", "notes": ""}
        return state

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if lines:
        new_steps = []
        idx = 1
        for line in lines:
            text = line
            if text[0].isdigit() and (text[1] in (".", ")")):
                text = text.split(".", 1)[1] if "." in text else text
            title = text[:60]
            step = type(state.steps[0]) if state.steps else None
            new_steps.append(type(state.steps[0])(**{"id": f"step_{idx}", "title": title, "description": text}) if state.steps else None)
            idx += 1
        if all(new_steps):
            from ..core.state import Step
            state.steps = [Step(id=f"step_{i+1}", title=s.title, description=s.description) for i, s in enumerate(new_steps)]
            state.current_index = 0 if state.steps else None
            state.reflection = {"status": "REPLACED", "notes": "Plan updated by reflection"}
    else:
        state.reflection = {"status": "UNKNOWN", "notes": raw[:512]}

    return state
