"""Audio types and protocols."""
from typing import Dict, Any, Optional, AsyncIterator, List
from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import Enum

from core.types.model import CoreBaseModel

class AudioProvider(str, Enum):
    """Audio provider types."""
    OPENAI = "openai"
    ASSEMBLYAI = "assemblyai"

class AudioFormat(str, Enum):
    """Audio format types."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"

class AudioQuality(str, Enum):
    """Audio quality levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TranscriptionMode(str, Enum):
    """Transcription modes."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"

class AudioChunk(BaseModel):
    """Audio chunk data."""
    data: bytes
    format: AudioFormat
    sample_rate: int
    channels: int
    duration: float
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

class TranscriptionOutput(CoreBaseModel):
    """Structured transcription output."""
    text: str
    confidence: float
    start_time: float
    end_time: float
    language: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True
    )

class TranscriptionResult(CoreBaseModel):
    """Complete transcription result with metadata."""
    text: str
    confidence: float
    start_time: float
    end_time: float
    duration: float
    language: Optional[str] = None
    is_final: bool = False
    speaker: Optional[str] = None
    words: Optional[List[Dict[str, Any]]] = None
    segments: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "language": self.language,
            "is_final": self.is_final,
            "speaker": self.speaker,
            "words": self.words,
            "segments": self.segments,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

class AudioConfig(CoreBaseModel):
    """Audio configuration model."""
    provider: AudioProvider = Field(default=AudioProvider.OPENAI)
    format: AudioFormat = Field(default=AudioFormat.WAV)
    quality: AudioQuality = Field(default=AudioQuality.MEDIUM)
    mode: TranscriptionMode = Field(default=TranscriptionMode.BATCH)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AudioProviderProtocol:
    """Protocol for audio providers."""

    async def initialize(self) -> None:
        """Initialize the provider."""
        raise NotImplementedError

    async def start(self) -> None:
        """Start the provider."""
        raise NotImplementedError

    async def stop(self) -> None:
        """Stop the provider."""
        raise NotImplementedError

    async def transcribe(
        self,
        audio: bytes,
        format: AudioFormat,
        sample_rate: int,
        channels: int,
        language: Optional[str] = None,
        **kwargs: Any
    ) -> TranscriptionResult:
        """Transcribe audio data.
        
        Args:
            audio: Audio data bytes
            format: Audio format
            sample_rate: Sample rate in Hz
            channels: Number of channels
            language: Optional language code
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Transcription result
            
        Raises:
            ValueError: If audio data is invalid
            RuntimeError: If transcription fails
        """
        raise NotImplementedError

    async def transcribe_stream(
        self,
        stream: AsyncIterator[AudioChunk],
        **kwargs: Any
    ) -> AsyncIterator[TranscriptionResult]:
        """Transcribe streaming audio data.
        
        Args:
            stream: Audio chunk stream
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Stream of transcription results
            
        Raises:
            ValueError: If stream data is invalid
            RuntimeError: If transcription fails
        """
        raise NotImplementedError

    async def check_health(self) -> Dict[str, Any]:
        """Check provider health.
        
        Returns:
            Health check results
        """
        raise NotImplementedError

class AudioInterview(CoreBaseModel):
    """Audio interview model."""
    
    id: UUID = Field(description="Interview ID")
    session_id: UUID = Field(description="Associated session ID")
    title: str = Field(description="Interview title")
    description: str = Field(description="Interview description")
    start_time: datetime = Field(description="Interview start time")
    end_time: Optional[datetime] = Field(default=None, description="Interview end time")
    duration: Optional[float] = Field(default=None, description="Total duration in seconds")
    audio_chunks: List[AudioChunk] = Field(default_factory=list, description="Audio chunks")
    transcript: Optional[str] = Field(default=None, description="Full transcript")
    quality: AudioQuality = Field(default=AudioQuality.MEDIUM, description="Audio quality")
    format: AudioFormat = Field(default=AudioFormat.WAV, description="Audio format")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Technical Interview - John Doe",
                "description": "Technical interview for Senior Software Engineer position",
                "start_time": "2024-03-20T10:00:00Z",
                "audio_chunks": [],
                "quality": "medium",
                "format": "wav",
                "metadata": {
                    "interview_type": "technical",
                    "difficulty": "medium",
                    "max_duration": 3600
                }
            }
        }
    }
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'AudioInterview':
        """Validate timestamp sequence."""
        if self.end_time and self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        if self.end_time and self.duration != (self.end_time - self.start_time).total_seconds():
            raise ValueError("Duration must match time difference")
        return self
    
    def add_chunk(self, chunk: AudioChunk) -> None:
        """Add audio chunk to interview.
        
        Args:
            chunk: Audio chunk to add
        """
        self.audio_chunks.append(chunk)
        if self.end_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
    
    def get_chunks_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[AudioChunk]:
        """Get chunks within time range.
        
        Args:
            start_time: Range start time
            end_time: Range end time
            
        Returns:
            List of chunks in range
        """
        return [
            chunk for chunk in self.audio_chunks
            if chunk.start_time >= start_time and chunk.end_time <= end_time
        ]
    
    def get_chunks_by_duration(
        self,
        min_duration: Optional[float] = None,
        max_duration: Optional[float] = None
    ) -> List[AudioChunk]:
        """Get chunks by duration range.
        
        Args:
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            
        Returns:
            List of chunks in duration range
        """
        return [
            chunk for chunk in self.audio_chunks
            if (min_duration is None or chunk.duration >= min_duration)
            and (max_duration is None or chunk.duration <= max_duration)
        ]
    
    def get_chunks_by_quality(
        self,
        quality: AudioQuality
    ) -> List[AudioChunk]:
        """Get chunks by quality level.
        
        Args:
            quality: Target quality level
            
        Returns:
            List of chunks with target quality
        """
        return [
            chunk for chunk in self.audio_chunks
            if chunk.quality == quality
        ]
    
    def get_chunks_by_format(
        self,
        format: AudioFormat
    ) -> List[AudioChunk]:
        """Get chunks by format.
        
        Args:
            format: Target format
            
        Returns:
            List of chunks with target format
        """
        return [
            chunk for chunk in self.audio_chunks
            if chunk.format == format
        ]
    
    def get_total_duration(self) -> float:
        """Get total duration of all chunks.
        
        Returns:
            Total duration in seconds
        """
        return sum(chunk.duration for chunk in self.audio_chunks)
    
    def get_total_size(self) -> int:
        """Get total size of all chunks.
        
        Returns:
            Total size in bytes
        """
        return sum(chunk.size_bytes for chunk in self.audio_chunks)
    
    def get_average_quality(self) -> AudioQuality:
        """Get average quality level.
        
        Returns:
            Average quality level
        """
        if not self.audio_chunks:
            return self.quality
            
        quality_values = {
            AudioQuality.LOW: 1,
            AudioQuality.MEDIUM: 2,
            AudioQuality.HIGH: 3
        }
        avg_value = sum(quality_values[chunk.quality] for chunk in self.audio_chunks) / len(self.audio_chunks)
        
        if avg_value < 1.5:
            return AudioQuality.LOW
        elif avg_value < 2.5:
            return AudioQuality.MEDIUM
        else:
            return AudioQuality.HIGH 