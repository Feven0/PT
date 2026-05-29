"""PromptSet schema for Weaviate."""
from typing import Dict, Any, List

from weaviate.classes.config import Property, DataType, Configure, Tokenization

from ..base import WeaviateSchemaBase

class PromptSetSchema(WeaviateSchemaBase):
    """Schema for prompt sets in Weaviate."""
    
    @classmethod
    def get_class_name(cls) -> str:
        """Get schema class name."""
        return "PromptSet"
        
    @classmethod
    def get_class_description(cls) -> str:
        """Get schema class description."""
        return "A collection of prompts used for various interactions like chat, interviews, and analysis"
        
    @classmethod
    def get_properties(cls) -> List[Property]:
        """Get schema properties."""
        return [
            Property(
                name="name",
                data_type=DataType.TEXT,
                description="Name of the prompt set",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="description",
                data_type=DataType.TEXT,
                description="Description of the prompt set",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="system_prompt",
                data_type=DataType.TEXT,
                description="System prompt for the interaction",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="user_prompts",
                data_type=DataType.TEXT_ARRAY,
                description="List of user prompts",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="interview_flow",
                data_type=DataType.OBJECT,
                description="Interview flow configuration",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="model_config",
                data_type=DataType.OBJECT,
                description="Model configuration",
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
        