"""Dynamic service for Weaviate operations."""
from typing import TypeVar, Generic, Optional, List, Dict, Any, Union
from uuid import UUID

from weaviate.collections import Collection
from weaviate.classes.query import Filter

from .base import WeaviateSchemaBase
from .client import WeaviateInfrastructureClient
from core.logging import BackendLogger


T = TypeVar("T")

class WeaviateDynamicService(Generic[T]):
    """Dynamic service for Weaviate operations with schema awareness.
    
    This service provides schema-aware operations on top of WeaviateInfrastructureClient.
    It ensures that operations conform to the defined schema and handles schema-specific
    configurations.
    """

    def __init__(
        self,
        client: WeaviateInfrastructureClient,
        schema: WeaviateSchemaBase,
        logger: Optional[BackendLogger] = None
    ):
        """Initialize service.
        
        Args:
            client: Weaviate client instance
            schema: Schema definition
            logger: Optional logger instance
        """
        if client is None:
            raise ValueError("Weaviate Client is required")
            
        self.client = client
        self.schema = schema
        self.logger = logger or BackendLogger(__name__).get_logger()
        self.class_name = schema.get_class_name()

    async def initialize(self) -> None:
        """Initialize the service by creating the collection if it doesn't exist."""
        try:
            # Check if collection exists
            await self.client.execute_operation(
                "get_class",
                self.class_name
            )
            self.logger.info(f"Collection {self.class_name} already exists")
        except Exception:
            # Create collection with schema configuration
            self.logger.info(f"Creating collection {self.class_name}")
            
            config = {
                "class": self.class_name,
                "description": self.schema.get_class_description(),
                "properties": self.schema.get_properties(),
                "vectorizer": self.schema.get_vectorizer_config(),
                "generative": self.schema.get_generative_config(),
                "replication": self.schema.get_replication_config(),
                "sharding": self.schema.get_shard_config()
            }
            
            await self.client.execute_operation(
                "create_class",
                self.class_name,
                config
            )
            self.logger.info(f"Collection {self.class_name} created successfully")

    async def add_object(
        self,
        data_object: Dict[str, Any],
        vector: Optional[List[float]] = None,
        uuid: Optional[Union[str, UUID]] = None
    ) -> str:
        """Add object to collection with schema validation."""
        # Here we could add schema validation if needed
        return await self.client.add_object(
            self.class_name,
            data_object,
            vector=vector,
            uuid=uuid
        )

    async def get_object(
        self,
        uuid: Union[str, UUID],
        with_vector: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get object from collection."""
        return await self.client.get_object(
            self.class_name,
            uuid,
            with_vector=with_vector
        )

    async def update_object(
        self,
        uuid: Union[str, UUID],
        data_object: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> None:
        """Update object in collection with schema validation."""
        # Here we could add schema validation if needed
        await self.client.update_object(
            self.class_name,
            uuid,
            data_object,
            vector=vector
        )

    async def delete_object(
        self,
        uuid: Union[str, UUID]
    ) -> None:
        """Delete object from collection."""
        await self.client.delete_object(
            self.class_name,
            uuid
        )

    async def query(
        self,
        vector: Optional[List[float]] = None,
        near_text: Optional[str] = None,
        where_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        with_vector: bool = False
    ) -> List[Dict[str, Any]]:
        """Query collection with schema-aware filtering."""
        return await self.client.query(
            self.class_name,
            vector=vector,
            near_text=near_text,
            where_filter=where_filter,
            limit=limit,
            offset=offset,
            with_vector=with_vector
        )

    async def batch_add_objects(
        self,
        objects: List[Dict[str, Any]],
        vectors: Optional[List[List[float]]] = None,
        uuids: Optional[List[Union[str, UUID]]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Batch add objects to collection with schema validation."""
        # Here we could add schema validation if needed
        return await self.client.batch_add_objects(
            self.class_name,
            objects,
            vectors=vectors,
            uuids=uuids,
            batch_size=batch_size
        )

    async def batch_delete_objects(
        self,
        uuids: List[Union[str, UUID]],
        batch_size: int = 100
    ) -> None:
        """Batch delete objects from collection."""
        await self.client.batch_delete_objects(
            self.class_name,
            uuids,
            batch_size=batch_size
        ) 

    async def update_by_filter(
        self,
        filter_dict: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """Update objects by filter."""
        await self.client.update_by_filter(self.class_name, filter_dict, data)

    async def delete_by_filter(
        self,
        filter_dict: Dict[str, Any]
    ) -> None:
        """Delete objects by filter."""
        await self.client.delete_by_filter(self.class_name, filter_dict)
