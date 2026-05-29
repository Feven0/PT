"""Base LLM interface."""
from typing import Dict, Any, Optional, List, AsyncIterator, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from pydantic import BaseModel

from core.types.llm import Message, ModelResponse
from core.types.model import CoreBaseModel
from core.config.llm_config import LLMConfig

class LLMError(Exception):
    """Base error for LLM operations."""
    
    def __init__(
        self,
        message: str,
        code: str = "llm_error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize error."""
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message": self.message,
            "code": self.code,
            "details": self.details
        }

T = TypeVar('T', bound=BaseModel)

class LLMProvider(ABC, Generic[T]):
    """Base class for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> ModelResponse[T]:
        """Generate completion from messages."""
        pass
        
    @abstractmethod
    async def stream(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> AsyncIterator[ModelResponse[T]]:
        """Stream completion from messages with optional structured output support."""
        pass
        
    @abstractmethod
    async def close(self) -> None:
        """Close the provider client."""
        pass

class LLMBase(ABC, Generic[T]):
    """Base class for LLM client."""
    
    def __init__(self, config: LLMConfig):
        """Initialize the client."""
        self.config = config
        #self.provider = self._create_provider()
        
    #@abstractmethod
    def _create_provider(self) -> LLMProvider[T]:
        """Create provider implementation."""
        pass
        
    async def generate(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> ModelResponse[T]:
        """Generate completion from messages."""
        return await self.provider.generate(
            messages=messages,
            functions=functions,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            metadata=metadata,
            response_model=response_model
        )
        
    async def stream(
        self,
        messages: List[Message],
        functions: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None
    ) -> AsyncIterator[ModelResponse[T]]:
        """Stream completion from messages with optional structured output support."""
        async for response in self.provider.stream(
            messages=messages,
            functions=functions,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            metadata=metadata,
            response_model=response_model
        ):
            yield response
            
    async def close(self) -> None:
        """Close the client."""
        await self.provider.close()

class BaseLLM(Generic[T]):
    """Base class for LLM implementations."""

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        metrics: Optional[Any] = None,
        logger: Optional[Any] = None
    ) -> None:
        """Initialize LLM.
        
        Args:
            name: LLM name
            config: LLM configuration
            metrics: Optional metrics manager
            logger: Optional logger
        """
        self._name = name
        self._config = config
        self._metrics = metrics
        self._logger = logger

    async def generate(
        self,
        messages: List[Message],
        **kwargs: Any
    ) -> ModelResponse[T]:
        """Generate completion for messages.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional generation arguments
            
        Returns:
            ModelResponse with generated completion
        """
        raise NotImplementedError

    async def stream(
        self,
        messages: List[Message],
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[T]]:
        """Stream completion for messages.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional generation arguments
            
        Yields:
            ModelResponse chunks with generated completion
        """
        raise NotImplementedError

    async def generate_with_functions(
        self,
        messages: List[Message],
        functions: List[Dict[str, Any]],
        **kwargs: Any
    ) -> ModelResponse[T]:
        """Generate completion with function calling.
        
        Args:
            messages: List of conversation messages
            functions: List of function definitions
            **kwargs: Additional generation arguments
            
        Returns:
            ModelResponse with generated completion and optional function call
        """
        raise NotImplementedError

    async def stream_with_functions(
        self,
        messages: List[Message],
        functions: List[Dict[str, Any]],
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[T]]:
        """Stream completion with function calling.
        
        Args:
            messages: List of conversation messages
            functions: List of function definitions
            **kwargs: Additional generation arguments
            
        Yields:
            ModelResponse chunks with generated completion and optional function call
        """
        raise NotImplementedError 