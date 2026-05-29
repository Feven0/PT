"""Audio configuration management."""
from typing import Dict, Optional, Any
from pydantic import Field

from core.types.model import CoreBaseModel
from core.types.audio import AudioProvider, AudioFormat, AudioQuality, TranscriptionMode
from .llm_config import LLMProviderConfig

class AudioConfig(CoreBaseModel):
    """Configuration for audio processing."""
    enabled: bool = Field(default=True, description="Enable audio processing")
    default_provider: AudioProvider = Field(
        default=AudioProvider.OPENAI,
        description="Default audio provider"
    )
    providers: Dict[str, LLMProviderConfig] = Field(
        default_factory=dict,
        description="Provider configurations"
    )
    format: AudioFormat = Field(
        default=AudioFormat.WAV,
        description="Default audio format"
    )
    quality: AudioQuality = Field(
        default=AudioQuality.MEDIUM,
        description="Default audio quality"
    )
    mode: TranscriptionMode = Field(
        default=TranscriptionMode.REAL_TIME,
        description="Default transcription mode"
    )
    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    chunk_size: int = Field(default=4096, description="Audio chunk size in bytes")
    vad_enabled: bool = Field(default=True, description="Enable voice activity detection")
    vad_threshold: float = Field(default=0.5, description="VAD threshold")
    noise_reduction: bool = Field(default=True, description="Enable noise reduction")
    max_duration: int = Field(default=300, description="Maximum audio duration in seconds")
    cache_audio: bool = Field(default=True, description="Enable audio caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds") 