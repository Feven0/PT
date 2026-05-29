"""User API models."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import Field, EmailStr
from uuid import UUID

from core.types.model import CoreBaseModel


class UserCreateDTO(CoreBaseModel):
    """User creation request DTO."""
    email: EmailStr = Field(description="User's email address")
    password: str = Field(description="User's password", min_length=8)
    name: str = Field(description="User's full name")
    role: str = Field(default="user", description="User's role")


class UserUpdateDTO(CoreBaseModel):
    """User update request DTO."""
    name: Optional[str] = Field(None, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="User's email address")
    password: Optional[str] = Field(None, description="User's password", min_length=8)
    role: Optional[str] = Field(None, description="User's role")
    is_active: Optional[bool] = Field(None, description="User's active status")


class UserResponseDTO(CoreBaseModel):
    """User response DTO."""
    id: UUID = Field(description="User ID")
    email: EmailStr = Field(description="User's email address")
    name: str = Field(description="User's full name")
    role: str = Field(description="User's role")
    is_active: bool = Field(description="Whether user is active")
    preferences: Dict = Field(default_factory=dict, description="User preferences")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class UserAuthRequestDTO(CoreBaseModel):
    """User authentication request DTO."""
    email: EmailStr = Field(description="User's email address")
    password: str = Field(description="User's password")


class UserAuthResponseDTO(CoreBaseModel):
    """User authentication response DTO."""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponseDTO = Field(description="User information") 