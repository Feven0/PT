"""Base classes for Weaviate schema definitions."""
from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod

import weaviate.classes.config as wc
from weaviate.classes.config import Property, DataType, Configure

class WeaviateSchemaBase(ABC):
    """Base class for Weaviate schema definitions."""
    
    @classmethod
    @abstractmethod
    def get_class_name(cls) -> str:
        """Get schema class name."""
        pass
        
    @classmethod
    @abstractmethod
    def get_class_description(cls) -> str:
        """Get schema class description."""
        pass
        
    @classmethod
    @abstractmethod
    def get_properties(cls) -> List[Property]:
        """Get schema properties as a list of Property objects."""
        pass
        
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
        
    @classmethod
    def get_schema_definition(cls) -> Dict[str, Any]:
        """Get complete schema definition."""
        return {
            "class": cls.get_class_name(),
            "description": cls.get_class_description(),
            "properties": cls.get_properties(),
            "vectorizer_config": cls.get_vectorizer_config(),
            "generative_config": cls.get_generative_config(),
            #"replicationConfig": cls.get_replication_config(),
            #"shardingConfig": cls.get_shard_config()
        }
        
    @classmethod
    def validate_property(
        cls,
        name: str,
        value: Any,
        property_def: Property
    ) -> bool:
        """Validate property value against definition."""
        data_type = property_def.data_type
        
        if data_type == DataType.TEXT and not isinstance(value, str):
            return False
        if data_type == DataType.INT and not isinstance(value, int):
            return False
        if data_type == DataType.NUMBER and not isinstance(value, (int, float)):
            return False
        if data_type == DataType.BOOLEAN and not isinstance(value, bool):
            return False
        if data_type == DataType.DATE and not isinstance(value, str):  # ISO date string
            return False
        if data_type == DataType.TEXT_ARRAY and not (isinstance(value, list) and all(isinstance(x, str) for x in value)):
            return False
            
        return True
        
    @classmethod
    def validate_object(cls, data: Dict[str, Any]) -> List[str]:
        """Validate object data against schema.
        
        Args:
            data: Object data to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        properties = cls.get_properties()
        
        # Check required properties
        for name, prop in properties.items():
            if prop.required and name not in data:
                errors.append(f"Missing required property: {name}")
                
        # Validate property values
        for name, value in data.items():
            if name not in properties:
                errors.append(f"Unknown property: {name}")
                continue
                
            if not cls.validate_property(name, value, properties[name]):
                errors.append(f"Invalid value for property: {name}")
                
        return errors 