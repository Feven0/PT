"""User types and protocols."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field, EmailStr

from core.types.model import CoreBaseModel


class UserState(str, Enum):
    """User state enumeration."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserRole(str, Enum):
    """User role enumeration."""
    
    USER = "user"
    ADMIN = "admin"


class User(CoreBaseModel):
    """User model."""
    
    email: EmailStr = Field(description="User email")
    name: str = Field(description="User name")
    password_hash: str = Field(description="Hashed password")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    state: UserState = Field(default=UserState.ACTIVE, description="User state")
    last_login_at: Optional[datetime] = Field(default=None, description="Last login timestamp")
    last_active_at: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def activate(self) -> None:
        """Activate user."""
        if self.state == UserState.DELETED:
            raise ValueError("Cannot activate deleted user")
            
        self.state = UserState.ACTIVE
        self.updated_at = datetime.now()
        
    def deactivate(self) -> None:
        """Deactivate user."""
        self.state = UserState.INACTIVE
        self.updated_at = datetime.now()
        
    def suspend(self) -> None:
        """Suspend user."""
        self.state = UserState.SUSPENDED
        self.updated_at = datetime.now()
        
    def delete(self) -> None:
        """Delete user."""
        self.state = UserState.DELETED
        self.updated_at = datetime.now()
        
    def record_login(self) -> None:
        """Record user login."""
        self.last_login_at = datetime.now()
        self.record_activity()
        
    def record_activity(self) -> None:
        """Record user activity."""
        self.last_active_at = datetime.now()
        
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences.
        
        Args:
            preferences: New preferences to update
        """
        self.preferences.update(preferences)
        self.updated_at = datetime.now()
        
    def is_active(self) -> bool:
        """Check if user is active.
        
        Returns:
            True if user is active
        """
        return self.state == UserState.ACTIVE
        
    def is_admin(self) -> bool:
        """Check if user is admin.
        
        Returns:
            True if user is admin
        """
        return self.role == UserRole.ADMIN
        
    def can_login(self) -> bool:
        """Check if user can login.
        
        Returns:
            True if user can login
        """
        return self.state == UserState.ACTIVE


class UserProfile(CoreBaseModel):
    """User profile model."""
    user_id: UUID = Field(description="User ID")
    name: str = Field(description="User name")
    email: str = Field(description="User email")
    role: UserRole = Field(description="User role")
    state: UserState = Field(description="User state")
    created_at: datetime = Field(description="User creation timestamp")
    updated_at: datetime = Field(description="User update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata") 