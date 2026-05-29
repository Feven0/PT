"""Analysis schema for Weaviate."""
from typing import Dict, Any, List

from weaviate.classes.config import Property, DataType, Configure, Tokenization

from ..base import WeaviateSchemaBase

class AnalysisSchema(WeaviateSchemaBase):
    """Schema for conversation analysis in Weaviate."""
    
    @classmethod
    def get_class_name(cls) -> str:
        """Get schema class name."""
        return "Analysis"
        
    @classmethod
    def get_class_description(cls) -> str:
        """Get schema class description."""
        return "Analysis of chat and interview sessions including topics, sentiment, and insights"
        
    @classmethod
    def get_properties(cls) -> List[Property]:
        """Get schema properties."""
        return [
            Property(
                name="session_id",
                data_type=DataType.TEXT,
                description="ID of the analyzed session",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="type",
                data_type=DataType.TEXT,
                description="Type of analysis (e.g., conversation, interview)",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="topics",
                data_type=DataType.TEXT_ARRAY,
                description="Main topics discussed",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="sentiment",
                data_type=DataType.OBJECT,
                description="Sentiment analysis results",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="insights",
                data_type=DataType.TEXT_ARRAY,
                description="Key insights from the analysis",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="summary",
                data_type=DataType.TEXT,
                description="Overall summary",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="recommendations",
                data_type=DataType.TEXT_ARRAY,
                description="Actionable recommendations",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="metrics",
                data_type=DataType.OBJECT,
                description="Quantitative metrics",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="metadata",
                data_type=DataType.OBJECT,
                description="Additional analysis metadata",
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