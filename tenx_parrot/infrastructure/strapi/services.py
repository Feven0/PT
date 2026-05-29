"""Strapi service factory."""
from typing import Dict, Optional, Type, TypeVar
from core.telemetry.metrics import MetricsManager
from .client import StrapiClient
from .dynamic import StrapiDynamicService, StrapiSchema
from .schemas import (
    IPersonaSession, IPersonaSessionSchema,
    IPersonaTrainee, IPersonaTraineeSchema,
    IPersonaJob, IPersonaJobSchema,
    IPersonaSessionOverallObserver, IPersonaSessionOverallObserverSchema,
    IPersonaSessionMessage, IPersonaSessionMessageSchema,
    IPersonaSessionObserver, IPersonaSessionObserverSchema,
    IPersonaAllUser, IPersonaAllUserSchema,
    IPersonaProfileInformation, IPersonaProfileInformationSchema,
    IPromptSet, IPromptSetSchema
)


T = TypeVar('T')


class StrapiServiceFactory:
    """Factory for creating Strapi services."""
    
    def __init__(
        self,
        client: StrapiClient,
        metrics: Optional[MetricsManager] = None
    ):
        self._client = client
        self._metrics = metrics
        self._services: Dict[Type[StrapiSchema], StrapiDynamicService] = {}
        
    def get_service(self, schema_cls: Type[StrapiSchema[T]]) -> StrapiDynamicService[T]:
        """Get or create a service for the given schema."""
        if schema_cls not in self._services:
            self._services[schema_cls] = StrapiDynamicService(
                client=self._client,
                schema_cls=schema_cls,
                metrics=self._metrics
            )
        return self._services[schema_cls]
        
    @property
    def session_service(self) -> StrapiDynamicService[IPersonaSession]:
        """Get the iPersona session service."""
        return self.get_service(IPersonaSessionSchema)
        
    @property
    def trainee_service(self) -> StrapiDynamicService[IPersonaTrainee]:
        """Get the iPersona trainee service."""
        return self.get_service(IPersonaTraineeSchema)
        
    @property
    def job_service(self) -> StrapiDynamicService[IPersonaJob]:
        """Get the iPersona job service."""
        return self.get_service(IPersonaJobSchema)
        
    @property
    def session_overall_observer_service(self) -> StrapiDynamicService[IPersonaSessionOverallObserver]:
        """Get the iPersona session overall observer service."""
        return self.get_service(IPersonaSessionOverallObserverSchema)
        
    @property
    def session_message_service(self) -> StrapiDynamicService[IPersonaSessionMessage]:
        """Get the iPersona session message service."""
        return self.get_service(IPersonaSessionMessageSchema)
        
    @property
    def session_observer_service(self) -> StrapiDynamicService[IPersonaSessionObserver]:
        """Get the iPersona session observer service."""
        return self.get_service(IPersonaSessionObserverSchema)
        
    @property
    def all_user_service(self) -> StrapiDynamicService[IPersonaAllUser]:
        """Get the iPersona all user service."""
        return self.get_service(IPersonaAllUserSchema)
        
    @property
    def profile_information_service(self) -> StrapiDynamicService[IPersonaProfileInformation]:
        """Get the iPersona profile information service."""
        return self.get_service(IPersonaProfileInformationSchema) 
    
    @property
    def prompt_service(self) -> StrapiDynamicService[IPromptSet]:
        """Get the iPersona prompt service."""
        return self.get_service(IPromptSetSchema)
