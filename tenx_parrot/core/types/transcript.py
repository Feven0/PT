"""Transcript types and protocols."""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID
from pydantic import Field, model_validator

from core.types.model import CoreBaseModel


class SpeakerType(str, Enum):
    """Speaker type enumeration."""
    INTERVIEWER = "interviewer"
    CANDIDATE = "candidate"
    SYSTEM = "system"


class TranscriptSegment(CoreBaseModel):
    """Transcript segment model."""
    
    id: UUID = Field(description="Segment ID")
    session_id: UUID = Field(description="Associated session ID")
    start_time: datetime = Field(description="Segment start time")
    end_time: datetime = Field(description="Segment end time")
    duration: float = Field(description="Segment duration in seconds")
    speaker: SpeakerType = Field(description="Speaker type")
    content: str = Field(description="Transcribed text")
    confidence: float = Field(description="Transcription confidence score", ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'TranscriptSegment':
        """Validate timestamp sequence."""
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        if self.duration != (self.end_time - self.start_time).total_seconds():
            raise ValueError("Duration must match time difference")
        return self


class Transcript(CoreBaseModel):
    """Transcript model."""
    
    id: UUID = Field(description="Transcript ID")
    session_id: UUID = Field(description="Associated session ID")
    title: str = Field(description="Transcript title")
    description: str = Field(description="Transcript description")
    start_time: datetime = Field(description="Transcript start time")
    end_time: Optional[datetime] = Field(default=None, description="Transcript end time")
    duration: Optional[float] = Field(default=None, description="Total duration in seconds")
    segments: List[TranscriptSegment] = Field(default_factory=list, description="Transcript segments")
    full_text: Optional[str] = Field(default=None, description="Full transcript text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Technical Interview - John Doe",
                "description": "Transcript of technical interview for Senior Software Engineer position",
                "start_time": "2024-03-20T10:00:00Z",
                "segments": [],
                "metadata": {
                    "interview_type": "technical",
                    "difficulty": "medium",
                    "language": "en"
                }
            }
        }
    }
    
    @model_validator(mode='after')
    def validate_timestamps(self) -> 'Transcript':
        """Validate timestamp sequence."""
        if self.end_time and self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        if self.end_time and self.duration != (self.end_time - self.start_time).total_seconds():
            raise ValueError("Duration must match time difference")
        return self
    
    def add_segment(self, segment: TranscriptSegment) -> None:
        """Add transcript segment.
        
        Args:
            segment: Transcript segment to add
        """
        if segment.session_id != self.session_id:
            raise ValueError("Segment session ID must match transcript session ID")
            
        self.segments.append(segment)
        self.updated_at = datetime.now(timezone.utc)
        
        # Update full text
        if self.full_text is None:
            self.full_text = segment.content
        else:
            self.full_text += f"\n{segment.content}"
    
    def get_segments_in_timeframe(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[TranscriptSegment]:
        """Get segments within time range.
        
        Args:
            start_time: Range start time
            end_time: Range end time
            
        Returns:
            List of segments in range
        """
        return [
            segment for segment in self.segments
            if segment.start_time >= start_time and segment.end_time <= end_time
        ]
    
    def get_segments_by_speaker(
        self,
        speaker: SpeakerType
    ) -> List[TranscriptSegment]:
        """Get segments by speaker type.
        
        Args:
            speaker: Target speaker type
            
        Returns:
            List of segments by speaker
        """
        return [
            segment for segment in self.segments
            if segment.speaker == speaker
        ]
    
    def complete(self) -> None:
        """Mark transcript as complete."""
        if not self.end_time:
            self.end_time = datetime.now(timezone.utc)
            self.duration = (self.end_time - self.start_time).total_seconds() 