"""WebSocket events for real-time updates."""
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class AnalysisUpdateEvent(BaseModel):
    """Base class for analysis update events."""
    session_id: str
    timestamp: datetime
    event_type: str

class RealtimeAnalysisEvent(AnalysisUpdateEvent):
    """Real-time analysis update event."""
    current_topic: str
    sentiment_score: float
    engagement_level: float
    key_points: list[str]
    alerts: list[Dict[str, Any]]

class SentimentUpdateEvent(AnalysisUpdateEvent):
    """Sentiment analysis update event."""
    overall_sentiment: float
    current_sentiment: float
    sentiment_change: float
    key_moments: Optional[list[Dict[str, Any]]]

class TopicUpdateEvent(AnalysisUpdateEvent):
    """Topic analysis update event."""
    current_topic: str
    topic_confidence: float
    topic_duration: float
    related_topics: list[str]

class EngagementUpdateEvent(AnalysisUpdateEvent):
    """Engagement analysis update event."""
    current_engagement: float
    attention_level: float
    interaction_quality: float
    engagement_trend: str

class PerformanceUpdateEvent(AnalysisUpdateEvent):
    """Performance analysis update event."""
    current_score: float
    competency_updates: Dict[str, float]
    recent_improvements: list[str]
    action_items: list[str]

# Event type mapping
ANALYSIS_EVENT_TYPES = {
    "realtime": RealtimeAnalysisEvent,
    "sentiment": SentimentUpdateEvent,
    "topic": TopicUpdateEvent,
    "engagement": EngagementUpdateEvent,
    "performance": PerformanceUpdateEvent
} 