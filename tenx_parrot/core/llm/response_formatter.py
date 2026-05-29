"""Response formatting for LLM chains."""
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.types.model import CoreBaseModel
from core.types.llm import (
    Message, 
    ModelResponse,
    ChainStep, 
    ChainState
)


class ChainResponse(CoreBaseModel):
    """Chain execution response."""
    chain_id: str
    name: Optional[str] = None
    status: str
    step_results: List[Dict[str, Any]]
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[Dict[str, Any]] = None

    model_config = {
        'from_attributes': True,
        'json_encoders': {
            datetime: lambda v: v.isoformat() if v else None
        }
    }
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()
        
    def to_dict(self) -> Dict[str, Any]:
        """Alias for dict() for compatibility."""
        return self.dict()

class ChainResponseFormatter:
    """Formats responses from chain execution."""
    
    def format_step_result(
        self,
        step: ChainStep,
        response: ModelResponse,
        messages: List[Message]
    ) -> Dict[str, Any]:
        """Format result from step execution."""
        return {
            "step_id": step.name,
            "status": step.status.value,
            "started_at": step.started_at.isoformat() if step.started_at else None,
            "completed_at": step.completed_at.isoformat() if step.completed_at else None,
            "duration": (step.completed_at - step.started_at).total_seconds() if (step.completed_at and step.started_at) else None,
            "result": {
                "content": response.content,
                "function_call": response.function_call.to_dict() if response.function_call else None,
                "metadata": response.metadata,
                "model": response.model,
                "usage": response.usage
            },
            "metadata": step.metadata,
            "error": step.error
        }
        
    def create_response(
        self,
        state: ChainState,
        step_results: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> ChainResponse:
        """Create chain response."""
        return ChainResponse(
            chain_id=state.chain_id,
            name=state.name,
            status=state.status.value,
            step_results=step_results,
            metadata={**(state.metadata or {}), **(metadata or {})},
            created_at=state.created_at,
            completed_at=state.completed_at,
            error=error
        )

    @staticmethod
    def format_chain_state(state: ChainState) -> Dict[str, Any]:
        """Format chain state."""
        return {
            "chain_id": state.chain_id,
            "name": state.name,
            "status": state.status.value,
            "current_step": state.current_step,
            "total_steps": len(state.steps),
            "completed_steps": len([s for s in state.steps if s.status.is_terminal()]),
            "metadata": state.metadata
        } 