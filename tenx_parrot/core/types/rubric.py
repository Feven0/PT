"""Core rubric type definitions."""
from __future__ import annotations
from typing import Dict, List, Optional, Any, ClassVar
from datetime import datetime, timezone
from uuid import UUID
from pydantic import Field, computed_field
from enum import Enum

from core.types.model import CoreBaseModel


class RubricMetricType(str, Enum):
    """Rubric metric type enumeration."""
    SCORE = "score"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"
    TEXT = "text"
    NUMERIC = "numeric"


class RubricMetric(CoreBaseModel):
    """Rubric metric definition."""
    id: str = Field(description="Metric ID")
    name: str = Field(description="Metric name")
    description: str = Field(description="Metric description")
    type: RubricMetricType = Field(description="Metric type")
    weight: float = Field(description="Metric weight", ge=0.0, le=1.0)
    min_value: Optional[float] = Field(default=None, description="Minimum value (for numeric metrics)")
    max_value: Optional[float] = Field(default=None, description="Maximum value (for numeric metrics)")
    options: Optional[List[str]] = Field(default=None, description="Options (for categorical metrics)")
    criteria: Optional[Dict[str, Any]] = Field(default=None, description="Evaluation criteria")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Rubric(CoreBaseModel):
    """Rubric definition for evaluations."""
    id: str = Field(description="Rubric ID")
    name: str = Field(description="Rubric name")
    description: str = Field(description="Rubric description")
    version: str = Field(description="Rubric version")
    metrics: List[RubricMetric] = Field(description="Evaluation metrics")
    category: str = Field(description="Rubric category")
    target_type: str = Field(description="Target type (interview, message, session, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Default rubrics cache
    _default_rubrics: ClassVar[Dict[str, Rubric]] = {}
    
    @classmethod
    def get_default_rubric(cls, rubric_id: Optional[str] = None) -> Optional[Rubric]:
        """Get default rubric by ID.
        
        If no ID is provided or the ID is not found, returns a generic default rubric.
        
        Args:
            rubric_id: Optional rubric ID
            
        Returns:
            Rubric instance or None
        """
        # Return cached rubric if available
        if rubric_id and rubric_id in cls._default_rubrics:
            return cls._default_rubrics[rubric_id]
            
        # Create a generic default rubric if no ID provided or not found
        if not rubric_id:
            rubric_id = "default"
            
        # Create a default rubric if not in cache
        if rubric_id not in cls._default_rubrics:
            cls._default_rubrics[rubric_id] = cls(
                id=rubric_id,
                name="Default Evaluation Rubric",
                description="Generic evaluation rubric with standard metrics",
                version="1.0",
                category="general",
                target_type="interview",
                metrics=[
                    RubricMetric(
                        id="clarity",
                        name="Clarity",
                        description="Clarity and coherence of responses",
                        type=RubricMetricType.SCORE,
                        weight=0.25,
                        min_value=0,
                        max_value=100,
                        criteria={
                            "excellent": "Responses are exceptionally clear, well-structured, and easy to understand",
                            "good": "Responses are clear and generally well-structured",
                            "average": "Responses are somewhat clear but may lack structure",
                            "poor": "Responses are unclear or difficult to follow"
                        }
                    ),
                    RubricMetric(
                        id="relevance",
                        name="Relevance",
                        description="Relevance of responses to questions",
                        type=RubricMetricType.SCORE,
                        weight=0.25,
                        min_value=0,
                        max_value=100,
                        criteria={
                            "excellent": "Responses directly address all aspects of the questions",
                            "good": "Responses address most aspects of the questions",
                            "average": "Responses partially address the questions",
                            "poor": "Responses do not address the questions"
                        }
                    ),
                    RubricMetric(
                        id="depth",
                        name="Depth",
                        description="Depth and thoroughness of responses",
                        type=RubricMetricType.SCORE,
                        weight=0.25,
                        min_value=0,
                        max_value=100,
                        criteria={
                            "excellent": "Responses show exceptional depth and thorough understanding",
                            "good": "Responses show good depth and understanding",
                            "average": "Responses show adequate depth",
                            "poor": "Responses lack depth or show superficial understanding"
                        }
                    ),
                    RubricMetric(
                        id="accuracy",
                        name="Accuracy",
                        description="Factual accuracy of responses",
                        type=RubricMetricType.SCORE,
                        weight=0.25,
                        min_value=0,
                        max_value=100,
                        criteria={
                            "excellent": "Responses are completely accurate with no errors",
                            "good": "Responses are mostly accurate with minor errors",
                            "average": "Responses contain some inaccuracies",
                            "poor": "Responses contain significant inaccuracies"
                        }
                    )
                ]
            )
            
        return cls._default_rubrics.get(rubric_id)
    
    def calculate_overall_score(self, metric_scores: Dict[str, float]) -> float:
        """Calculate overall score based on metric scores and weights.
        
        Args:
            metric_scores: Dictionary mapping metric IDs to scores
            
        Returns:
            Overall weighted score
        """
        if not metric_scores:
            return 0.0
            
        total_weight = 0.0
        weighted_sum = 0.0
        
        for metric in self.metrics:
            if metric.id in metric_scores and metric.type == RubricMetricType.SCORE:
                score = metric_scores[metric.id]
                weighted_sum += score * metric.weight
                total_weight += metric.weight
                
        if total_weight == 0:
            return 0.0
            
        return weighted_sum / total_weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rubric to dictionary.
        
        Returns:
            Dictionary representation of rubric
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "target_type": self.target_type,
            "metrics": [metric.dict() for metric in self.metrics],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        } 