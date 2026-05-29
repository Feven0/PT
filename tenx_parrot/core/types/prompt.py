"""Core prompt type definitions."""
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar, AsyncIterator, Literal
from datetime import datetime, timezone
from pydantic import Field, ConfigDict

from core.types.model import CoreBaseModel

T = TypeVar("T", bound=CoreBaseModel)

class PromptType(str, Enum):
    """Prompt type enumeration."""
    SYSTEM = "system"
    USER = "user"
    FUNCTION = "function"
    ASSISTANT = "assistant"
    INTERVIEW = "interview"
    ANALYSIS = "analysis"

PromptRole = Literal["system", "user", "assistant", "function"]

class PromptMessage(CoreBaseModel):
    """A single prompt message."""
    role: PromptRole = Field(description="Role of the message sender")
    content: str = Field(description="Content of the message")
    name: Optional[str] = Field(default=None, description="Name of the message sender")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message metadata")

class PromptTemplate(CoreBaseModel):
    """Template for generating prompts."""
    name: str = Field(description="Template name")
    description: Optional[str] = Field(default=None, description="Template description")
    messages: List[PromptMessage] = Field(description="List of template messages")
    output_model: Optional[Type[T]] = Field(default=None, description="Expected output model")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional template metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Template creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Template last update timestamp")

    def format(self, **kwargs: Any) -> List[PromptMessage]:
        """Format the template with variables.
        
        Args:
            **kwargs: Variables to format template with
            
        Returns:
            List of formatted messages
        """
        formatted = []
        for msg in self.messages:
            formatted.append(
                PromptMessage(
                    role=msg.role,
                    content=msg.content.format(**kwargs),
                    name=msg.name,
                    metadata=msg.metadata
                )
            )
        return formatted

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class LLMModelConfig(CoreBaseModel):
    """Model configuration."""
    model_name: str = Field(description="Name of the LLM model")
    provider: str = Field(description="Provider of the LLM model")
    temperature: float = Field(default=0.7, description="Temperature for sampling", ge=0.0, le=1.0)
    max_tokens: int = Field(default=500, description="Maximum tokens to generate", gt=0)
    top_p: float = Field(default=1.0, description="Top-p sampling parameter", ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty", ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, description="Presence penalty", ge=-2.0, le=2.0)
    stop_sequences: Optional[List[str]] = Field(default=None, description="Stop sequences")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional model metadata")

class PromptProviderProtocol(Protocol):
    """Protocol for prompt providers."""
    
    async def generate(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> T:
        """Generate a response from the prompt messages."""
        ...
    
    async def generate_stream(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> AsyncIterator[T]:
        """Generate a streaming response from the prompt messages."""
        ...
    
    def get_templates(self) -> Dict[str, Any]:
        """Get available prompt templates."""
        ...
    
    def register_template(
        self,
        template: Any
    ) -> None:
        """Register a new prompt template."""
        ...
    
    def format_template(
        self,
        template_name: str,
        **kwargs: Any
    ) -> List[PromptMessage]:
        """Format a prompt template with variables."""
        ...

class PromptSet(CoreBaseModel):
    """Prompt set configuration."""
    id: str = Field(description="Prompt set ID")
    name: str = Field(description="Prompt set name")
    description: str = Field(description="Prompt set description")
    system_prompt: str = Field(description="System prompt template")
    user_prompts: List[Dict[str, Any]] = Field(description="User prompt templates")
    llm_config: Optional[LLMModelConfig] = Field(default=None, description="LLM configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )
