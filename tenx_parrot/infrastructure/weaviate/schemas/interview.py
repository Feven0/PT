"""Interview schema for Weaviate."""
from typing import Dict, Any, List

from weaviate.classes.config import Property, DataType, Configure, Tokenization

from ..base import WeaviateSchemaBase

class InterviewSchema(WeaviateSchemaBase):
    """Schema for interview sessions in Weaviate."""
    
    @classmethod
    def get_class_name(cls) -> str:
        """Get schema class name."""
        return "Interview"
        
    @classmethod
    def get_class_description(cls) -> str:
        """Get schema class description."""
        return "A record of an interview session including questions, responses, and evaluations"
        
    @classmethod
    def get_properties(cls) -> List[Property]:
        """Get schema properties."""
        return [
            Property(
                name="session_id",
                data_type=DataType.TEXT,
                description="Unique identifier for the interview session",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="candidate_id",
                data_type=DataType.TEXT,
                description="Identifier of the interview candidate",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="prompt_set_id",
                data_type=DataType.TEXT,
                description="ID of the prompt set used for the interview",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=True,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="questions",
                data_type=DataType.TEXT_ARRAY,
                description="List of interview questions",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="responses",
                data_type=DataType.TEXT_ARRAY,
                description="List of candidate responses",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="evaluations",
                data_type=DataType.OBJECT_ARRAY,
                description="List of question-response evaluations",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="overall_score",
                data_type=DataType.NUMBER,
                description="Overall interview score",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="feedback",
                data_type=DataType.TEXT,
                description="Overall interview feedback",
                index_filterable=True,
                index_searchable=True,
                skip_vectorization=False,
                tokenization=Tokenization.WORD
            ),
            Property(
                name="metadata",
                data_type=DataType.OBJECT,
                description="Additional interview metadata",
                index_filterable=True,
                skip_vectorization=True
            ),
            Property(
                name="completed_at",
                data_type=DataType.DATE,
                description="Interview completion timestamp",
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