"""LLM types and protocols."""
from typing import Dict, Any, Optional, List, TypeVar, Generic, AsyncIterator, Type
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from core.types.model import CoreBaseModel

T = TypeVar('T', bound=BaseModel)

class Message(CoreBaseModel):
    """A message in a conversation."""
    role: str
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        clean_metadata = {}
        if self.metadata:
            clean_metadata = {k: v for k, v in self.metadata.items() 
                            if k not in ['messages', 'history', 'conversation', 'chain_state']}
        return {
            "role": self.role,
            "content": self.content,
            **({"name": self.name} if self.name else {}),
            **({"metadata": clean_metadata} if clean_metadata else {})
        }

class FunctionCall(CoreBaseModel):
    """Function call in a response."""
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    call_id: str

    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "arguments": self.arguments
        }

class ModelResponse(CoreBaseModel, Generic[T]):
    """Response from an LLM model with generic content type."""
    content: T
    function_call: Optional[FunctionCall] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "content": self.content if not isinstance(self.content, BaseModel) else self.content.model_dump(),
            "function_call": self.function_call.to_dict() if self.function_call else None,
            "metadata": self.metadata,
            "usage": self.usage,
            "model": self.model,
            "provider": self.provider
        }

class ChainStepStatus(str, Enum):
    """Chain step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class ChainStatus(str, Enum):
    """Chain status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class ChainStep(CoreBaseModel):
    """Chain step."""
    name: str
    description: str
    status: ChainStepStatus = ChainStepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }

class ChainState(CoreBaseModel):
    """Chain state."""
    chain_id: str
    name: str
    steps: List[ChainStep] = Field(default_factory=list)
    current_step: Optional[str] = None
    status: ChainStatus = ChainStatus.PENDING
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chain_id": self.chain_id,
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps],
            "current_step": self.current_step,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        } 