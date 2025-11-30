from __future__ import annotations
from typing import Callable, Optional
from .llm_connector import LMStudioConnector
from .llm_state import LLMCallState
from .errors import MissingLLMBindingError


class Layer1LLMEngine:
    """
    Main Layer-1 LLM Engine.
    - Bind LM Studio connector
    - Provides llm(prompt) -> str callable for Planner, Memory, or State Manager
    """

    def __init__(self):
        self._connector: Optional[LMStudioConnector] = None

    # ----------------- binding -----------------
    def bind_lmstudio(self, connector: LMStudioConnector) -> None:
        """Bind LM Studio connector"""
        self._connector = connector

    # ----------------- main API -----------------
    def llm(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """
        Main callable. Raises error if no connector bound.
        """
        if self._connector is None:
            raise MissingLLMBindingError("LM Studio connector not bound to LLM Engine")
        return self._connector.llm(prompt, max_tokens=max_tokens, temperature=temperature)

    # ----------------- helper -----------------
    def generate_call_state(self, prompt: str, metadata: dict = None) -> LLMCallState:
        """
        Create a new call state, run LLM, and mark completed.
        """
        state = LLMCallState.new(prompt, metadata)
        response = self.llm(prompt)
        state.mark_completed(response)
        return state
