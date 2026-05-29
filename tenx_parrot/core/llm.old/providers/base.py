"""Base LLM provider implementation."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, AsyncIterator

from core.types.model import CoreBaseModel
from core.types.prompt import PromptMessage
from core.config.llm_config import LLMProviderConfig

T = TypeVar("T", bound=CoreBaseModel)

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, name: str, config: LLMProviderConfig) -> None:
        """Initialize provider.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        self._name = name
        self._config = config

    @property
    def name(self) -> str:
        """Get provider name."""
        return self._name

    @property
    def config(self) -> LLMProviderConfig:
        """Get provider configuration."""
        return self._config

    async def generate(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> T:
        """Generate response from messages.
        
        Args:
            messages: List of prompt messages
            output_model: Optional output model for structured responses
            **kwargs: Additional arguments passed to provider
            
        Returns:
            Generated response
        """
        return await self._generate_impl(messages, output_model, **kwargs)

    async def generate_stream(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> AsyncIterator[T]:
        """Generate streaming response from messages.
        
        Args:
            messages: List of prompt messages
            output_model: Optional output model for structured responses
            **kwargs: Additional arguments passed to provider
            
        Returns:
            Generated response chunks
        """
        async for chunk in self._generate_stream_impl(messages, output_model, **kwargs):
            yield chunk

    @abstractmethod
    async def _generate_impl(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> T:
        """Implementation for generating responses."""
        raise NotImplementedError

    @abstractmethod
    async def _generate_stream_impl(
        self,
        messages: List[PromptMessage],
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> AsyncIterator[T]:
        """Implementation for generating streaming responses."""
        raise NotImplementedError 