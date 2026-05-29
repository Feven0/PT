"""Prompt repository implementation."""
from typing import Optional, List, Dict, Any, Union, Set
from datetime import datetime, timezone
from uuid import UUID

from core.types.base import ComponentNames as CN
from core.base.repository import BaseRepository
from core.config.base import AppConfig
from core.logging import BackendLogger
from core.telemetry.metrics import MetricsManager
from core.alert.manager import AlertManager
from core.cache.manager import CacheManager
from core.types.prompt import (
    PromptType,
    LLMModelConfig,
    PromptSet
)
from core.types.interview import InterviewFlow
from core.types.metrics import MetricType
from infrastructure.strapi.client import StrapiClient
from infrastructure.strapi.services import StrapiServiceFactory
from infrastructure.weaviate.client import WeaviateInfrastructureClient as WeaviateClient
from infrastructure.weaviate.dynamic import WeaviateDynamicService
from infrastructure.weaviate.schemas import get_schema
from core.errors.handlers import NotFoundError, ValidationError

class PromptError(Exception):
    """Base prompt error."""
    pass

class ConfigError(PromptError):
    """Configuration error."""
    pass

class PromptRepository(BaseRepository[PromptSet]):
    """Prompt repository implementation."""

    REQUIRED_CONFIG = {
        'cache_ttl': int,
        'batch_size': int,
        'max_retries': int
    }

    def __init__(
        self,
        name: str,
        config: AppConfig,
        strapi_client: StrapiClient,
        weaviate_client: WeaviateClient,
        metrics: Optional[MetricsManager] = None,
        cache: Optional[CacheManager] = None,  
        alert_manager: Optional[AlertManager] = None,
        logger: Optional[BackendLogger] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Initialize prompt repository."""
        super().__init__(
            name=name,
            config=config,
            metrics=metrics,
            cache=cache,
            logger=logger,
            dependencies=dependencies,
            required_config=self.REQUIRED_CONFIG
        )
        
        # Store clients
        self.strapi_client = strapi_client
        self.weaviate_client = weaviate_client
        
        # Store config
        self.cache_ttl = self._config.get('cache_ttl', 3600)
        self.batch_size = self._config.get('batch_size', 100)
        self.max_retries = self._config.get('max_retries', 3)
        
        # Initialize utilities
        self.metrics = metrics
        self.cache = cache
        self.alert_manager = alert_manager
        self.logger = logger or BackendLogger(__name__)
        
        # Initialize state
        self._prompt_sets: Dict[str, PromptSet] = {}

        # Initialize services
        self.strapi_service = StrapiServiceFactory(strapi_client, 
                                                   metrics)
        self.prompt_service = self.strapi_service.prompt_service

        self.weaviate_service = WeaviateDynamicService(
            client=weaviate_client,
            schema=get_schema("PromptSet"),
            logger=logger
        )        
        
    async def _initialize_impl(self) -> None:
        """Initialize repository."""
        await self.weaviate_service.initialize()
            
    async def create_prompt_set(
        self,
        name: str,
        description: str,
        system_prompt: str,
        user_prompts: List[Dict[str, Any]],
        interview_flow: Optional[InterviewFlow] = None,
        llm_config: Optional[LLMModelConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptSet:
        """Create a new prompt set."""
        try:
            # Create in Strapi
            prompt_data = {
                "name": name,
                "description": description,
                "systemPrompt": system_prompt,
                "userPrompts": user_prompts,
                "interviewFlow": interview_flow.to_dict() if interview_flow else None,
                "llmConfig": llm_config.to_dict() if llm_config else None,
                "metadata": metadata or {}
            }
            
            strapi_result = await self.prompt_service.create(prompt_data)
            
            # Create in Weaviate for search
            weaviate_data = {
                **prompt_data,
                "id": strapi_result["id"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            await self.weaviate_service.create(weaviate_data)
            
            # Create prompt set object
            prompt_set = PromptSet(
                id=strapi_result["id"],
                name=name,
                description=description,
                system_prompt=system_prompt,
                user_prompts=user_prompts,
                interview_flow=interview_flow,
                llm_config=llm_config,
                metadata=metadata or {},
                created_at=weaviate_data["created_at"],
                updated_at=weaviate_data["updated_at"]
            )
            
            # Store in cache
            self._prompt_sets[prompt_set.id] = prompt_set
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_prompt_set_created",
                    1,
                    labels={
                        "prompt_set_id": prompt_set.id,
                        "name": name
                    }
                )
                
            return prompt_set
            
        except Exception as e:
            self.logger.error(f"Failed to create prompt set: {str(e)}")
            raise PromptError(f"Failed to create prompt set: {str(e)}") from e
            
    async def get_prompt_set(
        self,
        prompt_set_id: Union[str, UUID]
    ) -> Optional[PromptSet]:
        """Get a prompt set by ID."""
        try:
            # Check cache first
            if str(prompt_set_id) in self._prompt_sets:
                return self._prompt_sets[str(prompt_set_id)]
                
            # Get from Strapi
            strapi_result = await self.prompt_service.get_by_id(str(prompt_set_id))
            if not strapi_result:
                return None
                
            # Create prompt set object
            prompt_set = PromptSet(
                id=strapi_result["id"],
                name=strapi_result["name"],
                description=strapi_result["description"],
                system_prompt=strapi_result["systemPrompt"],
                user_prompts=strapi_result["userPrompts"],
                interview_flow=InterviewFlow.from_dict(strapi_result["interviewFlow"]) if strapi_result.get("interviewFlow") else None,
                llm_config=LLMModelConfig.from_dict(strapi_result["llmConfig"]) if strapi_result.get("llmConfig") else None,
                metadata=strapi_result.get("metadata", {}),
                created_at=strapi_result.get("createdAt"),
                updated_at=strapi_result.get("updatedAt")
            )
            
            # Store in cache
            self._prompt_sets[prompt_set.id] = prompt_set
            
            return prompt_set
            
        except Exception as e:
            self.logger.error(f"Failed to get prompt set: {str(e)}")
            return None
            
    async def list_prompt_sets(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PromptSet]:
        """List prompt sets."""
        try:
            # Get from Weaviate for better search/filter capabilities
            results = await self.weaviate_service.list(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Convert to prompt sets
            return [
                PromptSet(
                    id=result["id"],
                    name=result["name"],
                    description=result["description"],
                    system_prompt=result["system_prompt"],
                    user_prompts=result["user_prompts"],
                    interview_flow=InterviewFlow.from_dict(result["interview_flow"]) if result.get("interview_flow") else None,
                    llm_config=LLMModelConfig.from_dict(result["llm_config"]) if result.get("llm_config") else None,
                    metadata=result.get("metadata", {}),
                    created_at=result.get("created_at"),
                    updated_at=result.get("updated_at")
                )
                for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list prompt sets: {str(e)}")
            return []
            
    async def update_prompt_set(
        self,
        prompt_set_id: Union[str, UUID],
        updates: Dict[str, Any]
    ) -> Optional[PromptSet]:
        """Update a prompt set."""
        try:
            # Update in Strapi
            strapi_result = await self.prompt_service.update(
                id=str(prompt_set_id),
                data=updates
            )
            
            if not strapi_result:
                return None
                
            # Update in Weaviate
            weaviate_data = {
                **updates,
                "updated_at": datetime.now().isoformat()
            }
            await self.weaviate_service.update(str(prompt_set_id), weaviate_data)
            
            # Create prompt set object
            prompt_set = PromptSet(
                id=strapi_result["id"],
                name=strapi_result["name"],
                description=strapi_result["description"],
                system_prompt=strapi_result["systemPrompt"],
                user_prompts=strapi_result["userPrompts"],
                interview_flow=InterviewFlow.from_dict(strapi_result["interviewFlow"]) if strapi_result.get("interviewFlow") else None,
                llm_config=LLMModelConfig.from_dict(strapi_result["llmConfig"]) if strapi_result.get("llmConfig") else None,
                metadata=strapi_result.get("metadata", {}),
                created_at=strapi_result.get("createdAt"),
                updated_at=strapi_result.get("updatedAt")
            )
            
            # Update cache
            self._prompt_sets[prompt_set.id] = prompt_set
            
            # Record metrics
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_prompt_set_updated",
                    1,
                    labels={
                        "prompt_set_id": prompt_set.id,
                        "updates": ",".join(list(updates.keys()))
                    }
                )
                
            return prompt_set
            
        except Exception as e:
            self.logger.error(f"Failed to update prompt set: {str(e)}")
            return None
            
    async def delete_prompt_set(
        self,
        prompt_set_id: Union[str, UUID]
    ) -> bool:
        """Delete a prompt set."""
        try:
            # Delete from both storages
            strapi_success = await self.prompt_service.delete(str(prompt_set_id))
            weaviate_success = await self.weaviate_service.delete(str(prompt_set_id))
            
            if strapi_success and weaviate_success:
                # Remove from cache
                self._prompt_sets.pop(str(prompt_set_id), None)
                
                # Record metrics
                if self.metrics:
                    self.metrics.record(
                        f"{self.name}_prompt_set_deleted",
                        1,
                        labels={"prompt_set_id": str(prompt_set_id)}
                    )
                    
            return strapi_success and weaviate_success
            
        except Exception as e:
            self.logger.error(f"Failed to delete prompt set: {str(e)}")
            return False
            
    async def get_interview_flow(
        self,
        prompt_set_id: Union[str, UUID]
    ) -> Optional[InterviewFlow]:
        """Get interview flow for a prompt set."""
        try:
            prompt_set = await self.get_prompt_set(prompt_set_id)
            return prompt_set.interview_flow if prompt_set else None
            
        except Exception as e:
            self.logger.error(f"Failed to get interview flow: {str(e)}")
            return None
            
    async def update_interview_flow(
        self,
        prompt_set_id: Union[str, UUID],
        interview_flow: InterviewFlow
    ) -> bool:
        """Update interview flow for a prompt set."""
        try:
            updates = {
                "interviewFlow": interview_flow.to_dict()
            }
            
            prompt_set = await self.update_prompt_set(prompt_set_id, updates)
            return bool(prompt_set)
            
        except Exception as e:
            self.logger.error(f"Failed to update interview flow: {str(e)}")
            return False
            
    async def get_llm_config(
        self,
        prompt_set_id: Union[str, UUID]
    ) -> Optional[LLMModelConfig]:
        """Get model configuration for a prompt set."""
        try:
            prompt_set = await self.get_prompt_set(prompt_set_id)
            return prompt_set.llm_config if prompt_set else None
            
        except Exception as e:
            self.logger.error(f"Failed to get model config: {str(e)}")
            return None
            
    async def update_llm_config(
        self,
        prompt_set_id: Union[str, UUID],
        llm_config: LLMModelConfig
    ) -> bool:
        """Update model configuration for a prompt set."""
        try:
            updates = {
                "llmConfig": llm_config.to_dict()
            }
            
            prompt_set = await self.update_prompt_set(prompt_set_id, updates)
            return bool(prompt_set)
            
        except Exception as e:
            self.logger.error(f"Failed to update model config: {str(e)}")
            return False

    async def search_prompt_sets(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PromptSet]:
        """Search prompt sets by content."""
        try:
            # Search in Weaviate
            results = await self.weaviate_service.search(
                query=query,
                properties=["name", "description", "system_prompt", "user_prompts"],
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Convert to prompt sets
            return [
                PromptSet(
                    id=result["id"],
                    name=result["name"],
                    description=result["description"],
                    system_prompt=result["system_prompt"],
                    user_prompts=result["user_prompts"],
                    interview_flow=InterviewFlow.from_dict(result["interview_flow"]) if result.get("interview_flow") else None,
                    llm_config=LLMModelConfig.from_dict(result["llm_config"]) if result.get("llm_config") else None,
                    metadata=result.get("metadata", {}),
                    created_at=result.get("created_at"),
                    updated_at=result.get("updated_at")
                )
                for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to search prompt sets: {str(e)}")
            return []

    async def get_prompt_set_version(
        self,
        prompt_set_id: str,
        version: str
    ) -> Optional[PromptSet]:
        """Get a specific version of a prompt set."""
        try:
            # Get from version history in Strapi
            version_data = await self.prompt_service.get_version(
                id=prompt_set_id,
                version=version
            )
            
            if not version_data:
                return None
                
            return PromptSet(
                id=version_data["id"],
                name=version_data["name"],
                description=version_data["description"],
                system_prompt=version_data["system_prompt"],
                user_prompts=version_data["user_prompts"],
                interview_flow=InterviewFlow.from_dict(version_data["interview_flow"]) if version_data.get("interview_flow") else None,
                llm_config=LLMModelConfig.from_dict(version_data["llm_config"]) if version_data.get("llm_config") else None,
                metadata=version_data.get("metadata", {}),
                created_at=version_data.get("created_at"),
                updated_at=version_data.get("updated_at")
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get prompt set version: {str(e)}")
            return None

    async def list_prompt_set_versions(
        self,
        prompt_set_id: str
    ) -> List[Dict[str, Any]]:
        """List all versions of a prompt set."""
        try:
            return await self.prompt_service.list_versions(prompt_set_id)
        except Exception as e:
            self.logger.error(f"Failed to list prompt set versions: {str(e)}")
            return []

    async def get_default_prompt_set(
        self,
        prompt_type: str
    ) -> Optional[PromptSet]:
        """Get default prompt set for a given type."""
        try:
            # Get from cache first
            cache_key = f"default_prompt_set:{prompt_type}"
            if self.cache:
                cached = await self.cache.get(cache_key)
                if cached:
                    return PromptSet.parse_raw(cached)
            
            # Search in Weaviate
            results = await self.weaviate_service.search(
                query="",
                filters={
                    "path": ["metadata.is_default", "metadata.type"],
                    "operator": "And",
                    "operands": [
                        {"value": True},
                        {"value": prompt_type}
                    ]
                },
                limit=1
            )
            
            if not results:
                return None
                
            prompt_set = PromptSet(
                id=results[0]["id"],
                name=results[0]["name"],
                description=results[0]["description"],
                system_prompt=results[0]["system_prompt"],
                user_prompts=results[0]["user_prompts"],
                interview_flow=InterviewFlow.from_dict(results[0]["interview_flow"]) if results[0].get("interview_flow") else None,
                llm_config=LLMModelConfig.from_dict(results[0]["llm_config"]) if results[0].get("llm_config") else None,
                metadata=results[0].get("metadata", {}),
                created_at=results[0].get("created_at"),
                updated_at=results[0].get("updated_at")
            )
            
            # Cache result
            if self.cache:
                await self.cache.set(
                    cache_key,
                    prompt_set.json(),
                    ttl=self.cache_ttl
                )
                
            return prompt_set
            
        except Exception as e:
            self.logger.error(f"Failed to get default prompt set: {str(e)}")
            return None 