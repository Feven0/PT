"""ChatSession schema for Weaviate."""
from typing import Dict, Any, List

from weaviate.classes.config import Property, DataType, Configure, Tokenization

from ..base import WeaviateSchemaBase

class ChatSessionSchema(WeaviateSchemaBase):
    """Schema for chat sessions in Weaviate."""
    
    @classmethod
    def get_class_name(cls) -> str:
        """Get schema class name."""
        return "ChatSession"
        
    @classmethod
    def get_class_description(cls) -> str:
        """Get schema class description."""
        return "A record of a chat session including messages, context, and analysis"
        
    @classmethod
    def get_properties(cls) -> List[Property]:
        """Get schema properties."""
        return [
            Property(
                name="session_id",
                data_type=DataType.TEXT,
                description="Unique identifier for the chat session",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="user_id",
                data_type=DataType.TEXT,
                description="Identifier of the chat user",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="prompt_set_id",
                data_type=DataType.TEXT,
                description="ID of the prompt set used for the chat",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="messages",
                data_type=DataType.TEXT_ARRAY,
                description="List of chat messages",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="context",
                data_type=DataType.OBJECT,
                description="Chat context and state",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="sentiment",
                data_type=DataType.OBJECT,
                description="Message sentiment analysis",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="topics",
                data_type=DataType.TEXT_ARRAY,
                description="Identified conversation topics",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="summary",
                data_type=DataType.TEXT,
                description="Conversation summary",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization="word"
            ),
            Property(
                name="metadata",
                data_type=DataType.OBJECT,
                description="Additional session metadata",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="ended_at",
                data_type=DataType.DATE,
                description="Session end timestamp",
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