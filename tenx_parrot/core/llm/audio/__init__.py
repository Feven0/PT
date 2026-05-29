"""Audio module for LLM integration."""

from .manager import AudioManager
from .provider import AudioProviderProtocol
from .providers.assembly import AssemblyAIProvider
from .providers.openai import OpenAIWhisperProvider

__all__ = [
    'AudioManager',
    'AudioProviderProtocol',
    'AssemblyAIProvider',
    'OpenAIWhisperProvider'
] 