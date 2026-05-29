"""LLM manager implementation."""
from typing import Any, Dict, List, Optional, Type, TypeVar, AsyncIterator

from core.base.manager import BaseManager
from core.types.model import CoreBaseModel
from core.types.prompt import PromptMessage, PromptTemplate
from core.config.llm_config import LLMConfig
from core.llm.providers.base import BaseLLMProvider
from core.llm.providers.openai import OpenAIProvider
from core.llm.providers.anthropic import AnthropicProvider

T = TypeVar("T", bound=CoreBaseModel)

class LLMManager(BaseManager):
    """Manager for LLM providers."""

    REQUIRED_CONFIG = {
        "enabled": bool,
        "default_provider": str,
        "providers": dict,
        "structured_output": bool,
        "cache_responses": bool,
        "cache_ttl": int,
        "max_retries": int,
        "timeout": int,
        "streaming_chunk_size": int,
        "max_context_length": int
    }

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        metrics: Optional[Any] = None,
        logger: Optional[Any] = None,
        dependencies: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize manager.
        
        Args:
            name: Manager name
            config: Manager configuration
            metrics: Optional metrics manager
            logger: Optional logger
            dependencies: Optional dependencies
        """
        super().__init__(name, config, metrics, logger, dependencies)
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._templates: Dict[str, PromptTemplate] = {}

    async def _initialize_impl(self) -> None:
        """Implementation for initialization."""
        # Initialize providers
        if "openai" in self._config["providers"]:
            self._providers["openai"] = OpenAIProvider(
                "openai",
                self._config["providers"]["openai"]
            )

        if "anthropic" in self._config["providers"]:
            self._providers["anthropic"] = AnthropicProvider(
                "anthropic",
                self._config["providers"]["anthropic"]
            )

        # Register metrics
        if self._metrics:
            self._metrics.register_counter(
                "llm_requests_total",
                "Total number of LLM requests",
                ["provider", "success"]
            )
            self._metrics.register_histogram(
                "llm_request_duration_seconds",
                "Duration of LLM requests in seconds",
                ["provider"]
            )
            self._metrics.register_counter(
                "llm_tokens_total",
                "Total number of tokens processed",
                ["provider", "direction"]
            )

    async def _start_impl(self) -> None:
        """Implementation for starting."""
        pass

    async def _stop_impl(self) -> None:
        """Implementation for stopping."""
        pass

    async def _check_health_impl(self) -> Dict[str, Any]:
        """Implementation for health check."""
        health = {
            "providers": {},
            "templates": len(self._templates)
        }

        for name, provider in self._providers.items():
            health["providers"][name] = {
                "enabled": provider.config.enabled,
                "model": provider.config.model
            }

        return health

    def register_template(self, template: PromptTemplate) -> None:
        """Register a prompt template.
        
        Args:
            template: Template to register
        """
        self._templates[template.name] = template

    def get_templates(self) -> Dict[str, PromptTemplate]:
        """Get registered templates.
        
        Returns:
            Dictionary of registered templates
        """
        return self._templates

    def format_template(
        self,
        template_name: str,
        **kwargs: Any
    ) -> List[PromptMessage]:
        """Format a template with variables.
        
        Args:
            template_name: Name of template to format
            **kwargs: Variables to format template with
            
        Returns:
            List of formatted prompt messages
        """
        if template_name not in self._templates:
            raise KeyError(f"Template {template_name} not found")
        return self._templates[template_name].format(**kwargs)

    async def generate(
        self,
        messages: List[PromptMessage],
        provider: Optional[str] = None,
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> T:
        """Generate response from messages.
        
        Args:
            messages: List of prompt messages
            provider: Optional provider name (uses default if not specified)
            output_model: Optional output model for structured responses
            **kwargs: Additional arguments passed to provider
            
        Returns:
            Generated response
        """
        provider_name = provider or self._config["default_provider"]
        if provider_name not in self._providers:
            raise ValueError(f"Provider {provider_name} not found")

        provider = self._providers[provider_name]
        if not provider.config.enabled:
            raise ValueError(f"Provider {provider_name} is not enabled")

        try:
            response = await provider.generate(messages, output_model, **kwargs)
            if self._metrics:
                self._metrics.increment_counter(
                    "llm_requests_total",
                    {"provider": provider_name, "success": "true"}
                )
            return response
        except Exception as e:
            if self._metrics:
                self._metrics.increment_counter(
                    "llm_requests_total",
                    {"provider": provider_name, "success": "false"}
                )
            raise

    async def generate_stream(
        self,
        messages: List[PromptMessage],
        provider: Optional[str] = None,
        output_model: Optional[Type[T]] = None,
        **kwargs: Any
    ) -> AsyncIterator[T]:
        """Generate streaming response from messages.
        
        Args:
            messages: List of prompt messages
            provider: Optional provider name (uses default if not specified)
            output_model: Optional output model for structured responses
            **kwargs: Additional arguments passed to provider
            
        Returns:
            Generated response chunks
        """
        provider_name = provider or self._config["default_provider"]
        if provider_name not in self._providers:
            raise ValueError(f"Provider {provider_name} not found")

        provider = self._providers[provider_name]
        if not provider.config.enabled:
            raise ValueError(f"Provider {provider_name} is not enabled")

        if not provider.config.streaming:
            raise ValueError(f"Streaming is not enabled for provider {provider_name}")

        try:
            async for chunk in provider.generate_stream(messages, output_model, **kwargs):
                if self._metrics:
                    self._metrics.increment_counter(
                        "llm_requests_total",
                        {"provider": provider_name, "success": "true"}
                    )
                yield chunk
        except Exception as e:
            if self._metrics:
                self._metrics.increment_counter(
                    "llm_requests_total",
                    {"provider": provider_name, "success": "false"}
                )
            raise 