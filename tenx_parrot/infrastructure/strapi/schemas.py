"""Strapi schema implementations."""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import Field
from pydantic import ConfigDict

from core.types.model import CoreBaseModel
from .dynamic import StrapiSchema


class IPersonaSession(CoreBaseModel):
    """iPersona session model."""
    id: str = Field(description="Session ID")
    slug: str = Field(description="Session slug")
    status: str = Field(description="Session status")
    attributes: Dict[str, Any] = Field(description="Session attributes")
    i_persona_observer_id: Optional[str] = Field(default=None, description="Observer ID")
    tinder_user_profile_id: Optional[str] = Field(default=None, description="User profile ID")
    tinder_job_profile_id: Optional[str] = Field(default=None, description="Job profile ID")


class IPersonaSessionSchema(StrapiSchema[IPersonaSession]):
    """Schema for iPersona sessions."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "iPersonaSessions"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "slug",
            "status",
            "attributes",
            "i_persona_observer { data { id } }",
            "tinder_user_profile { data { id } }",
            "tinder_job_profile { data { id } }"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaSession:
        attrs = data["attributes"]
        return IPersonaSession(
            id=data["id"],
            slug=attrs["slug"],
            status=attrs["status"],
            attributes=attrs["attributes"],
            i_persona_observer_id=attrs.get("i_persona_observer", {}).get("data", {}).get("id"),
            tinder_user_profile_id=attrs.get("tinder_user_profile", {}).get("data", {}).get("id"),
            tinder_job_profile_id=attrs.get("tinder_job_profile", {}).get("data", {}).get("id")
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaSession) -> Dict[str, Any]:
        data = {
            "slug": instance.slug,
            "status": instance.status,
            "attributes": instance.attributes
        }
        if instance.i_persona_observer_id:
            data["i_persona_observer"] = instance.i_persona_observer_id
        if instance.tinder_user_profile_id:
            data["tinder_user_profile"] = instance.tinder_user_profile_id
        if instance.tinder_job_profile_id:
            data["tinder_job_profile"] = instance.tinder_job_profile_id
        return data


class IPersonaTrainee(CoreBaseModel):
    """iPersona trainee model."""
    id: str
    attributes: Dict[str, Any]
    all_users_id: Optional[str] = None


class IPersonaTraineeSchema(StrapiSchema[IPersonaTrainee]):
    """Schema for iPersona trainees."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "tinderUserProfiles"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "attributes",
            "all_users { data { id } }"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaTrainee:
        attrs = data["attributes"]
        return IPersonaTrainee(
            id=data["id"],
            attributes=attrs["attributes"],
            all_users_id=attrs.get("all_users", {}).get("data", {}).get("id")
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaTrainee) -> Dict[str, Any]:
        data = {
            "attributes": instance.attributes
        }
        if instance.all_users_id:
            data["all_users"] = instance.all_users_id
        return data


class IPersonaJob(CoreBaseModel):
    """iPersona job model."""
    id: str
    attributes: Dict[str, Any]


class IPersonaJobSchema(StrapiSchema[IPersonaJob]):
    """Schema for iPersona jobs."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "tinderJobProfiles"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return ["attributes"]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaJob:
        attrs = data["attributes"]
        return IPersonaJob(
            id=data["id"],
            attributes=attrs["attributes"]
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaJob) -> Dict[str, Any]:
        return {
            "attributes": instance.attributes
        }



class IPersonaSessionOverallObserver(CoreBaseModel):
    """iPersona session overall observer model."""
    id: str
    attributes: Dict[str, Any]
    tinder_user_profile_id: Optional[str] = None
    tinder_job_profile_id: Optional[str] = None


class IPersonaSessionOverallObserverSchema(StrapiSchema[IPersonaSessionOverallObserver]):
    """Schema for iPersona session overall observers."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "iPersonaSessionOverallObservers"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "attributes",
            "tinder_user_profile { data { id } }",
            "tinder_job_profile { data { id } }"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaSessionOverallObserver:
        attrs = data["attributes"]
        return IPersonaSessionOverallObserver(
            id=data["id"],
            attributes=attrs["attributes"],
            tinder_user_profile_id=attrs.get("tinder_user_profile", {}).get("data", {}).get("id"),
            tinder_job_profile_id=attrs.get("tinder_job_profile", {}).get("data", {}).get("id")
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaSessionOverallObserver) -> Dict[str, Any]:
        data = {
            "attributes": instance.attributes
        }
        if instance.tinder_user_profile_id:
            data["tinder_user_profile"] = instance.tinder_user_profile_id
        if instance.tinder_job_profile_id:
            data["tinder_job_profile"] = instance.tinder_job_profile_id
        return data



class IPersonaSessionMessage(CoreBaseModel):
    """iPersona session message model."""
    id: str
    attributes: Dict[str, Any]
    i_persona_session_id: Optional[str] = None


class IPersonaSessionMessageSchema(StrapiSchema[IPersonaSessionMessage]):
    """Schema for iPersona session messages."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "iPersonaMessages"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "attributes",
            "i_persona_session { data { id } }"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaSessionMessage:
        attrs = data["attributes"]
        return IPersonaSessionMessage(
            id=data["id"],
            attributes=attrs["attributes"],
            i_persona_session_id=attrs.get("i_persona_session", {}).get("data", {}).get("id")
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaSessionMessage) -> Dict[str, Any]:
        data = {
            "attributes": instance.attributes
        }
        if instance.i_persona_session_id:
            data["i_persona_session"] = instance.i_persona_session_id
        return data


class IPersonaSessionObserver(CoreBaseModel):
    """iPersona session observer model."""
    id: str
    attributes: Dict[str, Any]
    i_persona_session_id: Optional[str] = None


class IPersonaSessionObserverSchema(StrapiSchema[IPersonaSessionObserver]):
    """Schema for iPersona session observers."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "iPersonaObservers"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "attributes",
            "i_persona_session { data { id } }"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaSessionObserver:
        attrs = data["attributes"]
        return IPersonaSessionObserver(
            id=data["id"],
            attributes=attrs["attributes"],
            i_persona_session_id=attrs.get("i_persona_session", {}).get("data", {}).get("id")
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaSessionObserver) -> Dict[str, Any]:
        data = {
            "attributes": instance.attributes
        }
        if instance.i_persona_session_id:
            data["i_persona_session"] = instance.i_persona_session_id
        return data


class IPersonaAllUser(CoreBaseModel):
    """iPersona all user model."""
    id: str
    name: str
    role: str
    batch: str
    email: Optional[str] = None
    password_hash: Optional[str] = None
    state: Optional[str] = "active"
    last_login_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IPersonaAllUserSchema(StrapiSchema[IPersonaAllUser]):
    """Schema for iPersona all users."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "allUsers"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "name",
            "role",
            "Batch",
            "email",
            "password_hash",
            "state",
            "last_login_at",
            "last_active_at",
            "preferences",
            "metadata"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaAllUser:
        attrs = data["attributes"]
        return IPersonaAllUser(
            id=data["id"],
            name=attrs["name"],
            role=attrs["role"],
            batch=attrs["Batch"],
            email=attrs.get("email"),
            password_hash=attrs.get("password_hash"),
            state=attrs.get("state", "active"),
            last_login_at=attrs.get("last_login_at"),
            last_active_at=attrs.get("last_active_at"),
            preferences=attrs.get("preferences", {}),
            metadata=attrs.get("metadata", {})
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaAllUser) -> Dict[str, Any]:
        data = {
            "name": instance.name,
            "role": instance.role,
            "Batch": instance.batch
        }
        
        # Add optional fields if they exist
        if instance.email is not None:
            data["email"] = instance.email
        if instance.password_hash is not None:
            data["password_hash"] = instance.password_hash
        if instance.state is not None:
            data["state"] = instance.state
        if instance.last_login_at is not None:
            data["last_login_at"] = instance.last_login_at
        if instance.last_active_at is not None:
            data["last_active_at"] = instance.last_active_at
        if instance.preferences:
            data["preferences"] = instance.preferences
        if instance.metadata:
            data["metadata"] = instance.metadata
            
        return data


class IPersonaProfileInformation(CoreBaseModel):
    """iPersona profile information model."""
    id: str
    gender: str
    nationality: str
    all_users_id: Optional[str] = None


class IPersonaProfileInformationSchema(StrapiSchema[IPersonaProfileInformation]):
    """Schema for iPersona profile information."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "profileInformations"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "gender",
            "nationality",
            "all_users { data { id } }"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPersonaProfileInformation:
        attrs = data["attributes"]
        return IPersonaProfileInformation(
            id=data["id"],
            gender=attrs["gender"],
            nationality=attrs["nationality"],
            all_users_id=attrs.get("all_users", {}).get("data", {}).get("id")
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPersonaProfileInformation) -> Dict[str, Any]:
        data = {
            "gender": instance.gender,
            "nationality": instance.nationality
        }
        if instance.all_users_id:
            data["all_users"] = instance.all_users_id
        return data


class IPromptSet(CoreBaseModel):
    """Prompt set model."""
    id: str
    name: str
    description: str
    system_prompt: str
    user_prompts: List[Dict[str, Any]] = Field(default_factory=list)
    interview_flow: Optional[Dict[str, Any]] = None
    llm_config: Optional[Dict[str, Any]] = None  # Renamed from model_config to avoid conflicts
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )


class IPromptSetSchema(StrapiSchema[IPromptSet]):
    """Schema for prompt sets."""
    
    @classmethod
    def get_collection_name(cls) -> str:
        return "promptSets"
        
    @classmethod
    def get_fields(cls) -> List[str]:
        return [
            "name",
            "description",
            "systemPrompt",
            "userPrompts",
            "interviewFlow",
            "llmConfig",
            "metadata"
        ]
        
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> IPromptSet:
        attrs = data["attributes"]
        return IPromptSet(
            id=data["id"],
            name=attrs["name"],
            description=attrs["description"],
            system_prompt=attrs["systemPrompt"],
            user_prompts=attrs["userPrompts"],
            interview_flow=attrs.get("interviewFlow"),
            llm_config=attrs.get("llmConfig"),
            metadata=attrs.get("metadata", {})
        )
        
    @classmethod
    def to_mutation_input(cls, instance: IPromptSet) -> Dict[str, Any]:
        data = {
            "name": instance.name,
            "description": instance.description,
            "systemPrompt": instance.system_prompt,
            "userPrompts": instance.user_prompts,
            "metadata": instance.metadata
        }
        if instance.interview_flow:
            data["interviewFlow"] = instance.interview_flow
        if instance.llm_config:
            data["llmConfig"] = instance.llm_config
        return data 