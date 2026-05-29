"""Dynamic Strapi service implementation."""
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from infrastructure.strapi.client import StrapiClient
from core.base.lifecycle import LifecycleAware
from core.telemetry.metrics import MetricsManager


T = TypeVar('T')


class StrapiSchema(ABC, Generic[T]):
    """Base class for Strapi schemas."""
    
    @classmethod
    @abstractmethod
    def get_collection_name(cls) -> str:
        """Get the collection name in Strapi."""
        pass
        
    @classmethod
    @abstractmethod
    def get_fields(cls) -> List[str]:
        """Get the list of fields to query."""
        pass
        
    @classmethod
    @abstractmethod
    def from_response(cls, data: Dict[str, Any]) -> T:
        """Convert Strapi response to model instance."""
        pass
        
    @classmethod
    @abstractmethod
    def to_mutation_input(cls, instance: T) -> Dict[str, Any]:
        """Convert model instance to mutation input."""
        pass


class StrapiDynamicService(LifecycleAware, Generic[T]):
    """Dynamic Strapi service implementation."""
    
    def __init__(
        self,
        client: StrapiClient,
        schema_cls: Type[StrapiSchema[T]],
        metrics: Optional[MetricsManager] = None
    ):
        self._client = client
        self._schema = schema_cls
        self._metrics = metrics
        
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
        
    async def start(self) -> None:
        """Start the service."""
        pass
        
    async def stop(self) -> None:
        """Stop the service."""
        pass
        
    def check_health(self) -> bool:
        """Check the health of the service."""
        return True
    
    def _build_query(
        self,
        operation: str,
        fields: List[str],
        variables: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        sort: Optional[List[str]] = None
    ) -> str:
        """Build a GraphQL query."""
        # Build field selection
        field_selection = ' '.join(fields)
        
        # Build variable definitions
        var_defs = []
        var_values = []
        
        if variables:
            for name, value in variables.items():
                var_defs.append(f"${name}: JSON")
                var_values.append(f"{name}: ${name}")
                
        if filters:
            var_defs.append("$filters: JSON")
            var_values.append("filters: $filters")
            
        if pagination:
            var_defs.append("$pagination: JSON")
            var_values.append("pagination: $pagination")
            
        if sort:
            var_defs.append("$sort: JSON")
            var_values.append("sort: $sort")
            
        # Build query
        query = f"""
        query {operation}({', '.join(var_defs)}) {{
            {self._schema.get_collection_name()}({', '.join(var_values)}) {{
                data {{
                    id
                    attributes {{
                        {field_selection}
                    }}
                }}
                meta {{
                    pagination {{
                        total
                        page
                        pageSize
                        pageCount
                    }}
                }}
            }}
        }}
        """
        
        return query
        
    def _build_mutation(
        self,
        operation: str,
        input_name: str,
        fields: List[str]
    ) -> str:
        """Build a GraphQL mutation."""
        # Build field selection
        field_selection = ' '.join(fields)
        
        # Build mutation
        mutation = f"""
        mutation {operation}($input: {input_name}) {{
            {operation}(data: $input) {{
                data {{
                    id
                    attributes {{
                        {field_selection}
                    }}
                }}
            }}
        }}
        """
        
        return mutation
        
    async def find_many(
        self,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        sort: Optional[List[str]] = None
    ) -> List[T]:
        """Find multiple records."""
        # Record metrics
        if self._metrics:
            self._metrics.record(
                "strapi_queries_total",
                1,
                labels={
                    "operation": "find_many",
                    "collection": self._schema.get_collection_name()
                }
            )
            
        # Build query
        query = self._build_query(
            operation="findMany",
            fields=self._schema.get_fields(),
            filters=filters,
            pagination=pagination,
            sort=sort
        )
        
        # Execute query
        variables = {}
        if filters:
            variables["filters"] = filters
        if pagination:
            variables["pagination"] = pagination
        if sort:
            variables["sort"] = sort
            
        result = await self._client.execute_query(query, variables)
        
        # Parse response
        collection_data = result[self._schema.get_collection_name()]
        return [
            self._schema.from_response(item)
            for item in collection_data["data"]
        ]
        
    async def find_one(
        self,
        id: str
    ) -> Optional[T]:
        """Find a single record by ID."""
        # Record metrics
        if self._metrics:
            self._metrics.record(
                "strapi_queries_total",
                1,
                labels={
                    "operation": "find_one",
                    "collection": self._schema.get_collection_name()
                }
            )
            
        # Build query
        query = self._build_query(
            operation="findOne",
            fields=self._schema.get_fields(),
            variables={"id": id}
        )
        
        # Execute query
        result = await self._client.execute_query(
            query,
            {"id": id}
        )
        
        # Parse response
        collection_data = result[self._schema.get_collection_name()]
        if not collection_data["data"]:
            return None
            
        return self._schema.from_response(collection_data["data"][0])
        
    async def create(
        self,
        instance: T
    ) -> T:
        """Create a new record."""
        # Record metrics
        if self._metrics:
            self._metrics.record(
                "strapi_mutations_total",
                labels={
                    "operation": "create",
                    "collection": self._schema.get_collection_name()
                }
            )
            
        # Build mutation
        mutation = self._build_mutation(
            operation="create",
            input_name=f"Create{self._schema.get_collection_name()}Input",
            fields=self._schema.get_fields()
        )
        
        # Execute mutation
        result = await self._client.execute_mutation(
            mutation,
            {"input": self._schema.to_mutation_input(instance)}
        )
        
        # Parse response
        collection_data = result[f"create{self._schema.get_collection_name()}"]
        return self._schema.from_response(collection_data["data"])
        
    async def update(
        self,
        id: str,
        instance: T
    ) -> T:
        """Update an existing record."""
        # Record metrics
        if self._metrics:
            self._metrics.record(
                "strapi_mutations_total",
                labels={
                    "operation": "update",
                    "collection": self._schema.get_collection_name()
                }
            )
            
        # Build mutation
        mutation = self._build_mutation(
            operation="update",
            input_name=f"Update{self._schema.get_collection_name()}Input",
            fields=self._schema.get_fields()
        )
        
        # Execute mutation
        variables = {
            "id": id,
            "input": self._schema.to_mutation_input(instance)
        }
        result = await self._client.execute_mutation(mutation, variables)
        
        # Parse response
        collection_data = result[f"update{self._schema.get_collection_name()}"]
        return self._schema.from_response(collection_data["data"])
        
    async def delete(
        self,
        id: str
    ) -> Optional[T]:
        """Delete a record."""
        # Record metrics
        if self._metrics:
            self._metrics.record(
                "strapi_mutations_total",
                labels={
                    "operation": "delete",
                    "collection": self._schema.get_collection_name()
                }
            )
            
        # Build mutation
        mutation = self._build_mutation(
            operation="delete",
            input_name=f"Delete{self._schema.get_collection_name()}Input",
            fields=self._schema.get_fields()
        )
        
        # Execute mutation
        result = await self._client.execute_mutation(
            mutation,
            {"id": id}
        )
        
        # Parse response
        collection_data = result[f"delete{self._schema.get_collection_name()}"]
        if not collection_data["data"]:
            return None
            
        return self._schema.from_response(collection_data["data"]) 