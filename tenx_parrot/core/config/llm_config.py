"""LLM configuration management."""
from typing import Dict, Optional, Any

from pydantic import Field

from core.types.model import CoreBaseModel

class LLMProviderConfig(CoreBaseModel):
    """Configuration for an LLM provider."""
    enabled: bool = Field(default=True, description="Enable this LLM provider")
    name: str = Field(default="", description="Provider name")
    api_key: str = Field(default="", description="API key for authentication")
    api_base: Optional[str] = Field(default=None, description="Base URL for API endpoint")
    model: str = Field(default="gpt-4", description="Model identifier")
    audio_model: str = Field(default="whisper-1", description="Audio model identifier")
    temperature: float = Field(default=0.7, description="Temperature for response generation")
    max_tokens: int = Field(default=2048, description="Maximum tokens in response")
    streaming: bool = Field(default=False, description="Enable streaming responses")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retries on failure")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

class AssemblyAIConfig(LLMProviderConfig):
    """AssemblyAI-specific configuration."""
    name: str = Field(default="assemblyai", description="Provider name")
    model: str = Field(default="assemblyai", description="AssemblyAI model identifier")
    audio_model: str = Field(default="assemblyai", description="AssemblyAI audio model identifier")
    api_base: str = Field(default="https://api.assemblyai.com/v1", description="AssemblyAI API endpoint")
    voice: str = Field(default="alloy", description="Voice for text-to-speech")

class OpenAIConfig(LLMProviderConfig):
    """OpenAI-specific configuration."""
    name: str = Field(default="openai", description="Provider name")
    model: str = Field(default="gpt-4", description="OpenAI model identifier")
    audio_model: str = Field(default="gpt-4o-audio-preview", description="OpenAI audio model identifier")
    api_base: str = Field(default="https://api.openai.com/v1", description="OpenAI API endpoint")
    voice: str = Field(default="alloy", description="Voice for text-to-speech")
    
class AnthropicConfig(LLMProviderConfig):
    """Anthropic-specific configuration."""
    name: str = Field(default="anthropic", description="Provider name")
    model: str = Field(default="claude-3-opus-20240229", description="Anthropic model identifier")
    audio_model: str = Field(default="claude-3-5-sonnet-20240620", description="Anthropic audio model identifier")
    api_base: str = Field(default="https://api.anthropic.com/v1", description="Anthropic API endpoint")
    voice: str = Field(default="alloy", description="Voice for text-to-speech")

class LLMConfig(CoreBaseModel):
    """Configuration for LLM services."""
    enabled: bool = Field(default=True, description="Enable LLM services")
    default_provider: str = Field(default="openai", description="Default LLM provider")
    providers: Dict[str, LLMProviderConfig] = Field(
        default_factory=lambda: {
            "openai": OpenAIConfig(),
            "anthropic": AnthropicConfig(),
            "assemblyai": AssemblyAIConfig()
        },
        description="LLM provider configurations"
    )
    structured_output: bool = Field(default=True, description="Enable structured output parsing")
    cache_responses: bool = Field(default=True, description="Enable response caching")
    cache_ttl: int = Field(default=3600, description="Global cache TTL in seconds")
    max_retries: int = Field(default=3, description="Global max retries")
    timeout: int = Field(default=30, description="Global timeout in seconds")
    streaming_chunk_size: int = Field(default=1024, description="Chunk size for streaming")
    max_context_length: int = Field(default=16384, description="Maximum context length") 