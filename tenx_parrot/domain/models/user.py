"""User domain models."""
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import Field, field_validator, EmailStr

from .base import BaseDomainModel


class Candidate(BaseDomainModel):
    """Candidate model."""
    email: EmailStr = Field(..., description="Email address")
    name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    resume_url: Optional[str] = Field(None, description="Resume URL")
    skills: List[str] = Field(default_factory=list, description="Skills list")
    experience_years: Optional[int] = Field(None, description="Years of experience")

    @classmethod
    @field_validator('experience_years', mode='before')
    def validate_experience(cls, v):
        if v is not None and v < 0:
            raise ValueError('Experience years cannot be negative')
        return v

    @classmethod
    @field_validator('name', mode='before')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class Interviewer(BaseDomainModel):
    """Interviewer model."""
    email: EmailStr = Field(..., description="Email address")
    name: str = Field(..., description="Full name")
    specialties: List[str] = Field(default_factory=list, description="Areas of expertise")
    availability: Dict[str, List[str]] = Field(default_factory=dict, description="Availability schedule")
    active: bool = Field(True, description="Active status")

    @classmethod
    @field_validator('name', mode='before')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @classmethod
    @field_validator('specialties', mode='before')
    def validate_specialties(cls, v):
        if not v:
            raise ValueError('At least one specialty is required')
        return v