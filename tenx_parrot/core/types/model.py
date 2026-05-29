"""Base model type definitions."""
from typing import Optional, Dict, Any, TypeVar, Generic, List
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel as PydanticBaseModel, ConfigDict, computed_field
from pydantic import Field, model_validator, field_validator


class CoreBaseModel(PydanticBaseModel):
    """Base model class for all core models.
    
    This is the foundational model class that all core models should inherit from.
    It provides common functionality like ID generation, timestamps, and serialization.
    """
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        from_attributes=True,  # Enables flexible attribute assignment
        populate_by_name=True,
        validate_assignment=False,
        strict=False,  # Stricter type checking
        frozen=False,  # Allow mutation
        revalidate_instances='always',  # Revalidate after updates
        str_strip_whitespace=True,
        str_to_lower=False,
        str_to_upper=False,
        use_enum_values=True,
        validate_default=True,
        extra='allow',  # Forbid extra attributes
        json_schema_extra={
            "examples": []
        },
        # Add this to ensure defaults are used
        populate_by_default=True
    )

    @model_validator(mode='before')
    def check_missing_fields(cls, data: Any) -> Any:
        """Initialize model with systematic default handling.
        
        This method:
        1. Gets all defined fields from the model
        2. Checks which fields have defaults
        3. Applies defaults for missing fields
        4. Handles special cases (like url -> id conversion)
        """
        # Get all field definitions from the model
        model_fields = cls.model_fields
        
        # # Handle special url -> id case
        # if 'url' in data and 'id' not in data:
        #     data['id'] = data['url'].split('/')[-1]
        
        # Process each defined field
        for field_name, field_info in model_fields.items():
            # Skip if field is already in data
            if field_name in data:
                if data[field_name]:
                    continue
                
            # Get default value if one exists
            if field_info.default_factory is not None:
                # Handle default_factory
                data[field_name] = field_info.default_factory()
            elif field_info.default is not None:
                # Handle simple default
                data[field_name] = field_info.default
        
        # return processed data
        return data
    
    @model_validator(mode='before')
    def set_defaults(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for id and timestamps if not provided."""
        if 'id' not in values:
            values['id'] = uuid4()
        if 'created_at' not in values:
            values['created_at'] = datetime.now(timezone.utc)
        if 'updated_at' not in values:
            values['updated_at'] = datetime.now(timezone.utc)
        return values
    
    @field_validator('created_at', 'updated_at')
    def validate_timestamps(cls, v: datetime) -> datetime:
        """Ensure timestamps are timezone-aware."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
    
    @computed_field
    def age(self) -> float:
        """Get model age in seconds."""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    def update(self, **kwargs: Any) -> None:
        """Update model fields with validation.
        
        Args:
            kwargs: Fields to update
        """
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.updated_at = datetime.now(timezone.utc)
        
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary with enhanced options.
        
        Returns:
            Model as dictionary
        """
        output = super().model_dump(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
            round_trip=True,  # New in v2: preserve types during serialization
            warnings=True,  # New in v2: show warnings for data loss
        )

        if not kwargs.get('core', True):
            output.pop('id')
            output.pop('created_at')
            output.pop('updated_at')
            
        return output
        
    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary with enhanced options.
        
        Returns:
            Model as dictionary
        """
        return self.model_dump(**kwargs)
    
    def model_dump_json(self, **kwargs) -> str:
        """Convert model to JSON string with enhanced options.
        
        Returns:
            Model as JSON string
        """
        def serialize_value(v: Any) -> Any:
            if isinstance(v, UUID):
                return str(v)
            if isinstance(v, datetime):
                return v.isoformat()
            return v
            
        return super().model_dump_json(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
            serialize_default=serialize_value,
            round_trip=True,  # New in v2: preserve types during serialization
            warnings=True,  # New in v2: show warnings for data loss
            **kwargs
        )
        
    @classmethod
    def model_validate_json(cls, data: str) -> "CoreBaseModel":
        """Create model from JSON string.
        
        Args:
            data: JSON string
            
        Returns:
            Created model
        """
        return super().model_validate_json(data)
    
    @classmethod
    def from_orm(cls, obj: Any) -> "CoreBaseModel":
        """Create model from ORM object.
        
        Args:
            obj: ORM object
            
        Returns:
            Created model
        """
        return cls.model_validate(obj)
    
    def copy_with(self, **kwargs: Any) -> "CoreBaseModel":
        """Create a copy with updated fields.
        
        Args:
            kwargs: Fields to update
            
        Returns:
            New model instance
        """
        data = self.model_dump()
        data.update(kwargs)
        return self.__class__.model_validate(data)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

class BaseModel(CoreBaseModel):
    """Base model with common functionality."""
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    def update(self, data: Dict[str, Any]) -> None:
        """Update model with new data."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc) 