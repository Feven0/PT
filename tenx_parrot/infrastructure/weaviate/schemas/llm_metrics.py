"""LLM metrics schema for Weaviate."""
from typing import Dict, Any, List

from weaviate.classes.config import Property, DataType, Configure, Tokenization

from ..base import WeaviateSchemaBase

class LLMMetricsSchema(WeaviateSchemaBase):
    """Schema for LLM metrics in Weaviate."""
    
    @classmethod
    def get_class_name(cls) -> str:
        """Get schema class name."""
        return "LLMMetrics"
        
    @classmethod
    def get_class_description(cls) -> str:
        """Get schema class description."""
        return "Metrics and performance data for Language Model operations"
        
    @classmethod
    def get_properties(cls) -> List[Property]:
        """Get schema properties."""
        return [
            Property(
                name="user_id",
                data_type=DataType.TEXT,
                description="User identifier",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="provider",
                data_type=DataType.TEXT,
                description="LLM provider name",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="model",
                data_type=DataType.TEXT,
                description="Model identifier",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="operation",
                data_type=DataType.TEXT,
                description="Operation type",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="metrics",
                data_type=DataType.OBJECT,
                description="Performance metrics",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="metadata",
                data_type=DataType.OBJECT,
                description="Additional metadata",
                index_filterable=True,
                skip_vectorization=True
            )
        ]
        
    @classmethod
    def get_vectorizer_config(cls) -> Configure.Vectorizer:
        """Get vectorizer configuration."""
        return Configure.Vectorizer.text2vec_openai(
            model="text-embedding-3-small",
            dimensions=1536,
            vectorize_collection_name=False
        )
        
    @classmethod
    def get_generative_config(cls) -> Configure.Generative:
        """Get generative configuration."""
        return Configure.Generative.openai()
        
    @classmethod
    def get_replication_config(cls) -> Dict[str, Any]:
        """Get replication configuration."""
        return {
            "factor": 3
        }
        
    @classmethod
    def get_shard_config(cls) -> Dict[str, Any]:
        """Get sharding configuration."""
        return {
            "desiredCount": 3,
            "actualCount": 3,
            "desiredVirtualCount": 128,
            "actualVirtualCount": 128,
            "key": "_id",
            "strategy": "hash",
            "function": "murmur3"
        } 