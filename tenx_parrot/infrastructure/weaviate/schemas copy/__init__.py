"""Weaviate schema registry."""
from typing import Dict, Type

from ..base import WeaviateSchemaBase
from .prompt_set import PromptSetSchema
from .chat_session import ChatSessionSchema
from .interview import InterviewSchema
from .analysis import AnalysisSchema
from .llm_metrics import LLMMetricsSchema

# Registry of all available schemas
SCHEMA_REGISTRY: Dict[str, Type[WeaviateSchemaBase]] = {
    "PromptSet": PromptSetSchema,
    "ChatSession": ChatSessionSchema,
    "Interview": InterviewSchema,
    "Analysis": AnalysisSchema,
    "LLMMetrics": LLMMetricsSchema
}

def get_schema(name: str) -> Type[WeaviateSchemaBase]:
    """Get schema by name.
    
    Args:
        name: Schema name
        
    Returns:
        Schema class
        
    Raises:
        KeyError: If schema not found
    """
    if name not in SCHEMA_REGISTRY:
        raise KeyError(f"Schema not found: {name}")
    return SCHEMA_REGISTRY[name]

def register_schema(name: str, schema: Type[WeaviateSchemaBase]) -> None:
    """Register new schema.
    
    Args:
        name: Schema name
        schema: Schema class
    """
    SCHEMA_REGISTRY[name] = schema 