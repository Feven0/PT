"""AssemblyAI provider implementation."""
import warnings

# Filter out the specific Pydantic deprecation warning from AssemblyAI
warnings.filterwarnings(
    "ignore",
    message="The `copy` method is deprecated; use `model_copy` instead",
    category=UserWarning
)

from typing import Any, AsyncIterator, Dict, Optional, List
import aiohttp
import asyncio
from datetime import datetime


import assemblyai as aai

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

class AssemblyAIProvider(AudioProviderProtocol):
    """AssemblyAI provider implementation."""

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        metrics: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        """Initialize provider with configuration."""
        self.name = name
        self.config = LLMProviderConfig(**config)
        self.metrics = metrics
        self.logger = logger
        self._session = None
        self._transcriber = None
        self._realtime_transcriber = None
        
        # Initialize AssemblyAI client
        aai.settings.api_key = self.config.api_key
        
        # Create transcriber instances
        self._transcriber = aai.Transcriber()
        
    async def initialize(self) -> None:
        """Initialize provider."""
        self._session = aiohttp.ClientSession(
            headers={"authorization": self.config.api_key}
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
        if self._realtime_transcriber:
            self._realtime_transcriber.close()
            self._realtime_transcriber = None

    async def check_health(self) -> Dict[str, Any]:
        """Check provider health."""
        try:
            if not self._session:
                return {
                    "status": "unhealthy",
                    "error": "Session not initialized"
                }
                
            async with self._session.get(f"{self.config.api_base}/status") as resp:
                if resp.status == 200:
                    return {
                        "status": "healthy",
                        "provider": "assemblyai",
                        "model": "assemblyai"
                    }
                return {
                    "status": "unhealthy",
                    "error": f"Status check failed with code {resp.status}"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def transcribe(
        self,
        audio: bytes,
        format: Optional[str] = None,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        **kwargs: Any
    ) -> ModelResponse[TranscriptionOutput]:
        """Transcribe audio data using AssemblyAI."""
        try:
            # Create transcription config
            config = aai.TranscriptionConfig(
                sample_rate=sample_rate or 16000,
                language_code=kwargs.get('language', 'en'),
                speaker_labels=kwargs.get('speaker_labels', False),
                **kwargs
            )
            
            # Upload and transcribe
            transcript = self._transcriber.transcribe(audio, config)
            
            if transcript.status == aai.TranscriptStatus.error:
                raise LLMError(f"Transcription failed: {transcript.error}")
            
            # Create metadata dictionary
            metadata = {
                "confidence": transcript.confidence or 1.0,
                "language": transcript.language_code,
                "audio_duration": transcript.audio_duration,
                "model": "assemblyai",
                "provider": "assemblyai"
            }
            
            # Add speaker labels if available
            if transcript.utterances:
                metadata["utterances"] = [
                    {
                        "speaker": u.speaker,
                        "text": u.text,
                        "start": u.start,
                        "end": u.end
                    } for u in transcript.utterances
                ]
            
            return ModelResponse[TranscriptionOutput](
                content=TranscriptionOutput(
                    text=transcript.text,
                    confidence=transcript.confidence or 1.0,
                    start_time=0.0,
                    end_time=transcript.audio_duration or 0.0,
                    language=transcript.language_code,
                    metadata=metadata
                ),
                metadata=metadata
            )
            
        except Exception as e:
            raise LLMError(f"Transcription failed: {str(e)}")

    async def transcribe_stream(
        self,
        stream: AsyncIterator[AudioChunk],
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[TranscriptionOutput]]:
        """Transcribe streaming audio data using AssemblyAI."""
        try:
            # Create realtime transcriber with callbacks
            async def on_open(session_opened: aai.RealtimeSessionOpened):
                if self.logger:
                    self.logger.info(f"Realtime session opened: {session_opened.session_id}")

            async def on_data(transcript: aai.RealtimeTranscript):
                if not transcript.text:
                    return

                metadata = {
                    "is_final": isinstance(transcript, aai.RealtimeFinalTranscript),
                    "model": "assemblyai",
                    "provider": "assemblyai"
                }

                yield ModelResponse[TranscriptionOutput](
                    content=TranscriptionOutput(
                        text=transcript.text,
                        confidence=1.0,  # Realtime doesn't provide confidence
                        start_time=transcript.start or 0.0,
                        end_time=transcript.end or 0.0,
                        language=kwargs.get('language', 'en'),
                        metadata=metadata
                    ),
                    metadata=metadata
                )

            async def on_error(error: aai.RealtimeError):
                if self.logger:
                    self.logger.error(f"Realtime transcription error: {error}")
                raise LLMError(f"Streaming transcription failed: {error}")

            async def on_close():
                if self.logger:
                    self.logger.info("Realtime session closed")

            self._realtime_transcriber = aai.RealtimeTranscriber(
                sample_rate=kwargs.get('sample_rate', 16000),
                on_data=on_data,
                on_error=on_error,
                on_open=on_open,
                on_close=on_close,
            )

            # Connect and stream
            self._realtime_transcriber.connect()
            
            try:
                async for chunk in stream:
                    await self._realtime_transcriber.stream(chunk.data)
            finally:
                self._realtime_transcriber.close()
                self._realtime_transcriber = None
                
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
        """Synthesize text to speech.
        
        Note: AssemblyAI doesn't currently support TTS
        """
        raise LLMError("Text-to-speech synthesis is not supported by AssemblyAI")

    async def synthesize_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[bytes]]:
        """Stream text to speech synthesis.
        
        Note: AssemblyAI doesn't currently support TTS
        """
        raise LLMError("Text-to-speech synthesis is not supported by AssemblyAI") 