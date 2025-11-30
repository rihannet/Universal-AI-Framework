class PlannerError(Exception):
    """Base exception for planner errors."""


class NodeExecutionError(PlannerError):
    """Raised when a node fails to execute cleanly."""


class MissingBindingError(PlannerError):
    """Raised when the planner is asked to run but required external binding(s) are not registered."""
