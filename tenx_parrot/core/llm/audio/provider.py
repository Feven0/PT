"""Audio provider interface."""
from typing import Any, AsyncIterator, Dict, Optional, Protocol
from abc import ABC, abstractmethod

from core.types.audio import (
    AudioChunk,
    AudioFormat,
    TranscriptionResult
)
from core.llm.base import LLMError, BaseLLM
from core.types.llm import (
    Message, 
    ModelResponse, 
)
from core.types.audio import TranscriptionOutput

class AudioProviderProtocol(Protocol):
    """Protocol for audio providers."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider."""
        pass
        
    @abstractmethod
    async def start(self) -> None:
        """Start the provider."""
        pass
        
    @abstractmethod
    async def stop(self) -> None:
        """Stop the provider."""
        pass
        
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check provider health."""
        pass
        
    @abstractmethod
    async def transcribe(
        self,
        audio: bytes,
        format: AudioFormat,
        sample_rate: int,
        channels: int,
        **kwargs: Any
    ) -> ModelResponse[TranscriptionOutput]:
        """Transcribe audio data."""
        pass
        
    @abstractmethod
    async def transcribe_stream(
        self,
        stream: AsyncIterator[AudioChunk],
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[TranscriptionOutput]]:
        """Transcribe streaming audio data."""
        pass

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> ModelResponse[bytes]:
        """Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            voice: Voice to use for synthesis
            format: Audio format for output
            sample_rate: Sample rate in Hz
            **kwargs: Additional synthesis arguments
            
        Returns:
            ModelResponse with audio data bytes
        """
        pass

    @abstractmethod
    async def synthesize_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[bytes]]:
        """Stream text to speech synthesis.
        
        Args:
            text: Text to synthesize
            voice: Voice to use for synthesis
            format: Audio format for output
            sample_rate: Sample rate in Hz
            **kwargs: Additional synthesis arguments
            
        Yields:
            ModelResponse chunks with audio data bytes
        """
        pass

class AudioProvider(BaseLLM[TranscriptionOutput]):
    """Base class for audio providers."""

    async def transcribe(
        self,
        audio: bytes,
        format: Optional[str] = None,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        **kwargs: Any
    ) -> ModelResponse[TranscriptionOutput]:
        """Transcribe audio data.
        
        Args:
            audio: Audio data bytes
            format: Audio format
            sample_rate: Sample rate in Hz
            channels: Number of channels
            **kwargs: Additional transcription arguments
            
        Returns:
            ModelResponse with transcription output
        """
        raise NotImplementedError

    async def transcribe_stream(
        self,
        stream: AsyncIterator[Any],
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[TranscriptionOutput]]:
        """Transcribe streaming audio data.
        
        Args:
            stream: Audio chunk stream
            **kwargs: Additional transcription arguments
            
        Yields:
            ModelResponse chunks with transcription output
        """
        raise NotImplementedError

    async def synthesize(
        self,
        text: str,
        **kwargs: Any
    ) -> ModelResponse[bytes]:
        """Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            **kwargs: Additional synthesis arguments
            
        Returns:
            ModelResponse with audio data bytes
        """
        raise NotImplementedError

    async def synthesize_stream(
        self,
        text: str,
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[bytes]]:
        """Stream text to speech synthesis.
        
        Args:
            text: Text to synthesize
            **kwargs: Additional synthesis arguments
            
        Yields:
            ModelResponse chunks with audio data bytes
        """
        raise NotImplementedError 