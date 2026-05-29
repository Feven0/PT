"""Agent state management."""
from enum import Enum

class AgentState(Enum):
    """States an agent can be in."""
    IDLE = "idle"
    GATHERING_CONTEXT = "gathering_context"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    ERROR = "error" 