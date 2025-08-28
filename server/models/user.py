"""
Pydantic models for user-related data structures.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserProvider(str, Enum):
    """Authentication providers."""
    ANONYMOUS = "anonymous"
    GOOGLE = "google"
    APPLE = "apple"
    EMAIL = "email"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserPreferences(BaseModel):
    """User preferences and settings."""
    language: str = "en"
    notification_enabled: bool = True
    voice_enabled: bool = True
    meditation_reminders: bool = False
    journal_reminders: bool = False
    crisis_support_enabled: bool = True
    preferred_voice: str = "Puck"


class UserProfile(BaseModel):
    """User profile information."""
    uid: str = Field(..., description="Firebase User ID")
    provider: UserProvider = UserProvider.ANONYMOUS
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    is_anonymous: bool = True
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    last_login: datetime
    preferences: UserPreferences = UserPreferences()
    total_sessions: int = 0
    last_mood_entry: Optional[datetime] = None


class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    preferences: Optional[UserPreferences] = None


class UpdateUserRequest(BaseModel):
    """Request model for updating user profile."""
    display_name: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class LinkAccountRequest(BaseModel):
    """Request model for linking anonymous account with permanent provider."""
    provider: UserProvider
    email: Optional[EmailStr] = None
    id_token: str = Field(..., description="Firebase ID token for verification")


class UserResponse(BaseModel):
    """Response model for user data."""
    uid: str
    provider: UserProvider
    email: Optional[str] = None
    display_name: Optional[str] = None
    is_anonymous: bool
    status: UserStatus
    created_at: datetime
    last_login: datetime
    preferences: UserPreferences
    total_sessions: int
    last_mood_entry: Optional[datetime] = None