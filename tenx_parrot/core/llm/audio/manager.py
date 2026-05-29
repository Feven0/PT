"""Audio manager implementation."""
from typing import Any, AsyncIterator, Dict, Optional, Type, Set
import asyncio
from datetime import datetime, timezone

from core.base.manager import BaseManager
from core.logging import BackendLogger
from core.config.base import AppConfig
from core.telemetry.metrics import MetricsManager
from .providers.assembly import AssemblyAIProvider
from .providers.openai import OpenAIWhisperProvider
from ..client import LLMClient
from core.types.llm import ModelResponse
from core.types.audio import (
    AudioChunk,
    AudioFormat,
    AudioProvider,
    AudioProviderProtocol,
    TranscriptionMode,
    TranscriptionResult
)


from core.config.audio_config import AudioConfig
from core.types.components import HealthStatus
from core.types.metrics import MetricType

class AudioManager(BaseManager):
    """Manager for audio processing and transcription."""

    REQUIRED_CONFIG = {
        "enabled": bool,
        "default_provider": str,
        "providers": dict,
        "format": str,
        "quality": str,
        "mode": str,
        "sample_rate": int,
        "channels": int,
        "chunk_size": int,
        "vad_enabled": bool,
        "vad_threshold": float,
        "noise_reduction": bool,
        "max_duration": int,
        "cache_audio": bool,
        "cache_ttl": int
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        metrics: Optional[MetricsManager] = None,
        llm_client: Optional[LLMClient] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None,        
    ) -> None:
        """Initialize manager.
        
        Args:
            name: Manager name
            config: Manager configuration
            metrics: Optional metrics manager
            logger: Optional logger
            dependencies: Optional dependencies
            llm_client: Optional LLM client for transcription/synthesis
        """
        
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            logger=logger,
            dependencies=dependencies
        )
        self._providers: Dict[str, AudioProviderProtocol] = {}
        self._active_streams: Dict[str, asyncio.Task] = {}
        self._llm_client = llm_client

    async def _initialize_impl(self) -> None:
        """Implementation for initialization."""
        # Initialize providers
        for provider_name, provider_config in self._config["providers"].items():
            if not provider_config.get("enabled", True):
                continue

            try:
                provider_cls = self._get_provider_class(provider_name)
                provider = provider_cls(
                    name=f"{self.name}.{provider_name}",
                    config=provider_config,
                    metrics=self._metrics,
                    logger=self._logger
                )
                await provider.initialize()
                self._providers[provider_name] = provider

                if self._logger:
                    self._logger.info(f"Initialized audio provider: {provider_name}")
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Failed to initialize provider {provider_name}: {str(e)}")
                self._health_status.update(
                    status=HealthStatus.UNHEALTHY, 
                    details={"provider": provider_name, "error": str(e)}
                )

        # Register metrics
        if self._metrics:
            self._metrics.register_metric(
                name=f"{self.name}_transcriptions_total",
                type=MetricType.COUNTER,
                description="Total number of audio transcriptions",
                labels={"provider": "provider", 
                        "mode": "mode", 
                        "success": "success"},
                component=self.name
            )
            self._metrics.register_metric(
                name=f"{self.name}_duration_seconds",
                type=MetricType.HISTOGRAM,
                description="Duration of audio in seconds",
                labels={"provider": "provider"},
                component=self.name
            )
            self._metrics.register_metric(
                name=f"{self.name}_transcription_latency_seconds",
                type=MetricType.HISTOGRAM,
                description="Latency of transcription in seconds",
                labels={"provider": "provider", "mode": "mode"},
                component=self.name
            )
            self._metrics.register_metric(
                name=f"{self.name}_bytes_total",
                type=MetricType.COUNTER,
                description="Total number of audio bytes processed",
                labels={"provider": "provider"},
                component=self.name
            )

    async def _start_impl(self) -> None:
        """Implementation for starting."""
        for provider in self._providers.values():
            await provider.start()

    async def _stop_impl(self) -> None:
        """Implementation for stopping."""
        # Cancel active streams
        for stream_id, task in self._active_streams.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Stop providers
        for provider in self._providers.values():
            await provider.stop()

    async def _check_health_impl(self) -> Dict[str, Any]:
        """Implementation for health check."""
        health = {
            "providers": {},
            "active_streams": len(self._active_streams)
        }

        for name, provider in self._providers.items():
            try:
                provider_health = await provider.check_health()
                health["providers"][name] = provider_health
            except Exception as e:
                health["providers"][name] = {"error": str(e)}

        return health

    def _get_provider_class(self, provider_name: str) -> Type[AudioProviderProtocol]:
        """Get provider class by name.
        
        Args:
            provider_name: Provider name
            
        Returns:
            Provider class
            
        Raises:
            ValueError: If provider not found
        """
        print('audio provider_name', provider_name)
        if provider_name == AudioProvider.ASSEMBLYAI:  
            return AssemblyAIProvider
        elif provider_name == AudioProvider.OPENAI:            
            return OpenAIWhisperProvider
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    async def transcribe(
        self,
        audio: bytes,
        format: Optional[AudioFormat] = None,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> TranscriptionResult:
        """Transcribe audio data.
        
        Args:
            audio: Audio data bytes
            format: Audio format
            sample_rate: Sample rate in Hz
            channels: Number of channels
            provider: Provider to use
            **kwargs: Additional provider-specific arguments
            
        Returns:
            TranscriptionResult with the transcribed text and metadata
        """
        if self._llm_client is not None:
            # Use LLM client for transcription when available
            return await self._llm_client.transcribe(
                audio=audio,
                format=format,
                sample_rate=sample_rate,
                channels=channels,
                **kwargs
            )

        # Default to provider-based transcription
        if not provider:
            provider = self._config["default_provider"]

        if provider not in self._providers:
            raise ValueError(f"Provider {provider} not found")

        provider_instance = self._providers[provider]
        return await provider_instance.transcribe(
            audio=audio,
            format=format,
            sample_rate=sample_rate,
            channels=channels,
            **kwargs
        )

    async def transcribe_stream(
        self,
        stream: AsyncIterator[AudioChunk],
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[TranscriptionResult]:
        """Transcribe streaming audio data.
        
        Args:
            stream: Audio chunk stream
            provider: Provider to use
            **kwargs: Additional provider-specific arguments
            
        Yields:
            TranscriptionResult with transcribed text and metadata for each chunk
        """
        if self._llm_client is not None:
            # Use LLM client for streaming transcription when available
            async for result in self._llm_client.transcribe_stream(stream, **kwargs):
                yield result
            return

        # Default to provider-based streaming transcription
        if not provider:
            provider = self._config["default_provider"]

        if provider not in self._providers:
            raise ValueError(f"Provider {provider} not found")

        provider_instance = self._providers[provider]
        async for result in provider_instance.transcribe_stream(stream, **kwargs):
            yield result

    async def process_stream(
        self,
        stream_id: str,
        stream: AsyncIterator[AudioChunk],
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Process audio stream in background.
        
        Args:
            stream_id: Unique stream identifier
            stream: Audio chunk stream
            provider: Optional provider name (uses config default if not specified)
            **kwargs: Additional provider-specific arguments
            
        Raises:
            ValueError: If stream ID already exists
            RuntimeError: If stream processing fails
        """
        if stream_id in self._active_streams:
            raise ValueError(f"Stream ID already exists: {stream_id}")

        async def process():
            try:
                async for result in self.transcribe_stream(stream, provider, **kwargs):
                    # Handle result (e.g., send to websocket, save to database)
                    pass
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Stream processing failed: {str(e)}")
            finally:
                self._active_streams.pop(stream_id, None)

        self._active_streams[stream_id] = asyncio.create_task(process())

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> ModelResponse[bytes]:
        """Synthesize text to speech.
        
        Args:
            text: Text to synthesize
            voice: Voice to use for synthesis
            format: Audio format for output
            sample_rate: Sample rate in Hz
            provider: Provider to use
            **kwargs: Additional provider-specific arguments
            
        Returns:
            ModelResponse with audio data bytes
        """
        if self._llm_client is not None:
            # Use LLM client for synthesis when available
            return await self._llm_client.synthesize(
                text=text,
                voice=voice,
                format=format,
                sample_rate=sample_rate,
                **kwargs
            )

        # Default to provider-based synthesis
        if not provider:
            provider = self._config["default_provider"]

        if provider not in self._providers:
            raise ValueError(f"Provider {provider} not found")

        provider_instance = self._providers[provider]
        return await provider_instance.synthesize(
            text=text,
            voice=voice,
            format=format,
            sample_rate=sample_rate,
            **kwargs
        )

    async def synthesize_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        format: AudioFormat = AudioFormat.MP3,
        sample_rate: int = 24000,
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[ModelResponse[bytes]]:
        """Stream text to speech synthesis.
        
        Args:
            text: Text to synthesize
            voice: Voice to use for synthesis
            format: Audio format for output
            sample_rate: Sample rate in Hz
            provider: Provider to use
            **kwargs: Additional provider-specific arguments
            
        Yields:
            ModelResponse chunks with audio data bytes
        """
        if self._llm_client is not None:
            # Use LLM client for streaming synthesis when available
            async for chunk in self._llm_client.synthesize_stream(
                text=text,
                voice=voice,
                format=format,
                sample_rate=sample_rate,
                **kwargs
            ):
                yield chunk
            return

        # Default to provider-based streaming synthesis
        if not provider:
            provider = self._config["default_provider"]

        if provider not in self._providers:
            raise ValueError(f"Provider {provider} not found")

        provider_instance = self._providers[provider]
        async for chunk in provider_instance.synthesize_stream(
            text=text,
            voice=voice,
            format=format,
            sample_rate=sample_rate,
            **kwargs
        ):
            yield chunk 