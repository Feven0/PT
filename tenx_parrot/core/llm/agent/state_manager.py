"""State management for tools and agents."""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
from core.base.manager import BaseManager

logger = logging.getLogger(__name__)

@dataclass
class ToolState:
    """State for a tool instance."""
    tool_id: str
    status: str = "idle"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_operation: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager(BaseManager):
    """Manages state for tools and agents."""
    
    def __init__(self):
        """Initialize state manager."""
        super().__init__()
        self.tool_states: Dict[str, ToolState] = {}
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Initialize the state manager."""
        self.initialized = True
        logger.info("State manager initialized")
        
    async def cleanup(self) -> None:
        """Clean up state manager."""
        self.tool_states.clear()
        self.agent_states.clear()
        self.initialized = False
        logger.info("State manager cleaned up")
        
    def get_tool_state(self, tool_id: str) -> Optional[ToolState]:
        """Get state for a tool."""
        return self.tool_states.get(tool_id)
        
    def set_tool_state(
        self,
        tool_id: str,
        status: Optional[str] = None,
        operation: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolState:
        """Set state for a tool."""
        state = self.tool_states.get(tool_id)
        if not state:
            state = ToolState(tool_id=tool_id)
            self.tool_states[tool_id] = state
            
        if status:
            state.status = status
            if status == "running":
                state.start_time = datetime.now()
                state.end_time = None
                state.error = None
            elif status in ("completed", "failed"):
                state.end_time = datetime.now()
                
        if operation is not None:
            state.current_operation = operation
            
        if error is not None:
            state.error = error
            
        if metadata:
            state.metadata.update(metadata)
            
        return state
        
    def clear_tool_state(self, tool_id: str) -> None:
        """Clear state for a tool."""
        self.tool_states.pop(tool_id, None)
        
    def get_agent_state(
        self,
        agent_id: str,
        key: Optional[str] = None
    ) -> Any:
        """Get state for an agent."""
        state = self.agent_states.get(agent_id, {})
        if key is not None:
            return state.get(key)
        return state
        
    def set_agent_state(
        self,
        agent_id: str,
        key: str,
        value: Any
    ) -> None:
        """Set state for an agent."""
        if agent_id not in self.agent_states:
            self.agent_states[agent_id] = {}
        self.agent_states[agent_id][key] = value
        
    def clear_agent_state(
        self,
        agent_id: str,
        key: Optional[str] = None
    ) -> None:
        """Clear state for an agent."""
        if key is not None and agent_id in self.agent_states:
            self.agent_states[agent_id].pop(key, None)
        else:
            self.agent_states.pop(agent_id, None)
            
    def list_active_tools(self) -> Dict[str, ToolState]:
        """List all tools with active state."""
        return {
            tool_id: state
            for tool_id, state in self.tool_states.items()
            if state.status == "running"
        } 