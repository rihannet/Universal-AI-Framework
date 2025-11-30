from __future__ import annotations


class LLMEngineError(Exception):
    """Base exception for LLM engine errors."""


class MissingLLMBindingError(LLMEngineError):
    """Raised when LM Studio or LLM connector is not bound."""
