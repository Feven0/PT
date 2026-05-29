"""OpenAI Whisper provider implementation."""
from typing import Any, AsyncIterator, Dict, Optional, List
import aiohttp
import asyncio
from datetime import datetime
import instructor
from litellm import Router

from core.types.audio import (
    AudioChunk,
    AudioFormat,
    TranscriptionResult
)
from core.llm.audio.provider import AudioProviderProtocol
from core.types.audio import TranscriptionOutput
from core.llm.base import LLMError
from core.types.llm import (
    Message, 
    ModelResponse
)
from core.config.llm_config import LLMProviderConfig

class OpenAIWhisperProvider(AudioProviderProtocol):
    """OpenAI Whisper provider implementation."""

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        metrics: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        """Initialize provider with litellm configuration."""
        self.name = name
        self.config = LLMProviderConfig(**config)
        self.metrics = metrics
        self.logger = logger
        self._session = None
        
        # Initialize instructor client with litellm settings
        client_config = {
            "model": self.config.audio_model,
            "api_key": self.config.api_key,
            "timeout": self.config.timeout,
            "base_url": self.config.api_base or "https://api.openai.com/v1"
        }
        
        # https://docs.litellm.ai/docs/routing
        self.aclient = instructor.patch(
            Router(
                model_list=[
                    {
                        "model_name": self.config.audio_model,
                        "litellm_params": client_config,
                    }
                ],
                default_litellm_params={"acompletion": True},
            )
        )

    async def initialize(self) -> None:
        """Initialize provider."""
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.config.api_key}"}
        )

    async def start(self) -> None:
        """Start provider."""
        if not self._session:
            await self.initialize()

    async def stop(self) -> None:
        """Stop provider."""
        if self._session:
            await self._session.close()
            self._session = None

    async def check_health(self) -> Dict[str, Any]:
        """Check provider health."""
        try:
            if not self._session:
                return {
                    "status": "unhealthy",
                    "error": "Session not initialized"
                }
                
            # OpenAI doesn't have a dedicated health check endpoint
            # We'll use a minimal transcription request to test
            test_audio = b"test"  # Minimal audio data
            try:
                await self.transcribe(test_audio, AudioFormat.WAV, 16000, 1)
                return {
                    "status": "healthy",
                    "provider": "openai",
                    "model": self.config.audio_model
                }
            except Exception as e:
                if "Invalid audio file" in str(e):
                    # This is expected since we sent invalid audio
                    return {
                        "status": "healthy",
                        "provider": "openai",
                        "model": self.config.audio_model
                    }
                return {
                    "status": "unhealthy",
                    "error": str(e)
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def transcribe(
        self,
        audio: bytes,
        format: AudioFormat,
        sample_rate: int,
        channels: int,
        **kwargs: Any
    ) -> ModelResponse[TranscriptionOutput]:
        """Transcribe audio data using OpenAI Whisper."""
        try:
            # Prepare transcription request
            params = {
                "file": ("audio", audio, f"audio/{format.value}"),
                "model": self.config.audio_model,
                "response_format": "verbose_json",
                **kwargs
            }
            
            # Use instructor for structured output
            response = await self.aclient.chat.completions.create(
                response_model=TranscriptionOutput,
                messages=[{"role": "system", "content": "Transcribe the audio"}],
                model=self.config.audio_model,
                **params
            )
            
            # Create metadata dictionary with all available information
            metadata = {
                "confidence": response.confidence,
                "start_time": response.start_time,
                "end_time": response.end_time,
                "model": self.config.audio_model,
                "provider": "openai"
            }
            if hasattr(response, "metadata"):
                metadata.update(response.metadata or {})
            
            return ModelResponse[TranscriptionOutput](
                content=response,
                metadata=metadata
            )
            
        except Exception as e:
            raise LLMError(f"Transcription failed: {str(e)}")

    async def transcribe_stream(
        self,
        stream: AsyncIterator[AudioChunk],
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[TranscriptionOutput]]:
        """Transcribe streaming audio data using OpenAI Whisper."""
        try:
            buffer = bytearray()
            chunk_duration = 0
            
            async for chunk in stream:
                buffer.extend(chunk.data)
                chunk_duration += chunk.duration
                
                # Process in ~30 second chunks (Whisper's recommended segment length)
                if chunk_duration >= 30:
                    # Use instructor for structured output
                    response = await self.aclient.chat.completions.create(
                        response_model=TranscriptionOutput,
                        messages=[{"role": "system", "content": "Process streaming audio"}],
                        model=self.config.audio_model,
                        stream=True,
                        file=("audio", bytes(buffer), f"audio/{chunk.format.value}"),
                        **kwargs
                    )
                    
                    # Create metadata dictionary with all available information
                    metadata = {
                        "confidence": response.confidence,
                        "start_time": response.start_time,
                        "end_time": response.end_time,
                        "is_final": True,
                        "model": self.config.audio_model,
                        "provider": "openai"
                    }
                    if hasattr(response, "metadata"):
                        metadata.update(response.metadata or {})
                    
                    yield ModelResponse[TranscriptionOutput](
                        content=response,
                        metadata=metadata
                    )
                    
                    # Reset buffer
                    buffer.clear()
                    chunk_duration = 0
                    
            # Process any remaining audio
            if buffer:
                response = await self.aclient.chat.completions.create(
                    response_model=TranscriptionOutput,
                    messages=[{"role": "system", "content": "Process final audio chunk"}],
                    model=self.config.audio_model,
                    stream=True,
                    file=("audio", bytes(buffer), f"audio/{chunk.format.value}"),
                    **kwargs
                )
                
                # Create metadata dictionary with all available information
                metadata = {
                    "confidence": response.confidence,
                    "start_time": response.start_time,
                    "end_time": response.end_time,
                    "is_final": True,
                    "model": self.config.audio_model,
                    "provider": "openai"
                }
                if hasattr(response, "metadata"):
                    metadata.update(response.metadata or {})
                
                yield ModelResponse[TranscriptionOutput](
                    content=response,
                    metadata=metadata
                )
                
        except Exception as e:
            raise LLMError(f"Streaming transcription failed: {str(e)}")

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> ModelResponse[bytes]:
        """Synthesize text to speech using OpenAI TTS.
        
        Args:
            text: Text to synthesize
            voice: Voice to use for synthesis (alloy, echo, fable, onyx, nova, or shimmer)
            format: Audio format for output
            sample_rate: Sample rate in Hz
            **kwargs: Additional synthesis arguments
            
        Returns:
            ModelResponse with audio data bytes
        """
        try:
            # Prepare synthesis parameters
            params = {
                "input": text,
                "voice": voice or "alloy",  # Default to alloy voice if not specified
                "model": kwargs.get("model", "tts-1"),
                "response_format": format.value,
                "speed": kwargs.get("speed", 1.0),
                **kwargs
            }
            
            # Use instructor for structured output
            response = await self.aclient.audio.speech.create(**params)
            
            # Create metadata dictionary with all available information
            metadata = {
                "format": format.value,
                "sample_rate": sample_rate,
                "voice": params["voice"],
                "model": params["model"],
                "provider": "openai"
            }
            if hasattr(response, "metadata"):
                metadata.update(response.metadata or {})
            
            return ModelResponse[bytes](
                content=response.content,
                metadata=metadata
            )
            
        except Exception as e:
            raise LLMError(f"Audio synthesis failed: {str(e)}")

    async def synthesize_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[bytes]]:
        """Stream text to speech synthesis using OpenAI TTS.
        
        Args:
            text: Text to synthesize
            voice: Voice to use for synthesis (alloy, echo, fable, onyx, nova, or shimmer)
            format: Audio format for output
            sample_rate: Sample rate in Hz
            **kwargs: Additional synthesis arguments
            
        Yields:
            ModelResponse chunks with audio data bytes
        """
        try:
            # Split text into sentences or chunks for streaming
            chunks = self._split_text_into_chunks(text)
            
            for chunk in chunks:
                # Prepare synthesis parameters for chunk
                params = {
                    "input": chunk,
                    "voice": voice or "alloy",  # Default to alloy voice if not specified
                    "model": kwargs.get("model", "tts-1"),
                    "response_format": format.value,
                    "speed": kwargs.get("speed", 1.0),
                    **kwargs
                }
                
                # Use instructor for structured output
                response = await self.aclient.audio.speech.create(**params)
                
                # Create metadata dictionary with all available information
                metadata = {
                    "format": format.value,
                    "sample_rate": sample_rate,
                    "voice": params["voice"],
                    "model": params["model"],
                    "is_final": False,
                    "provider": "openai"
                }
                if hasattr(response, "metadata"):
                    metadata.update(response.metadata or {})
                
                yield ModelResponse[bytes](
                    content=response.content,
                    metadata=metadata
                )
                
        except Exception as e:
            raise LLMError(f"Streaming audio synthesis failed: {str(e)}")

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks for streaming synthesis.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        # Simple sentence-based splitting
        # Could be enhanced with more sophisticated chunking strategies
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()] 