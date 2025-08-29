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


class AgeGroup(str, Enum):
    """Age group categories."""
    TEEN = "13-17"
    YOUNG_ADULT = "18-24"
    ADULT = "25-34"
    MATURE_ADULT = "35+"


class Gender(str, Enum):
    """Gender options for personalized responses."""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class VoiceType(str, Enum):
    """Available voice options."""
    PUCK = "Puck"
    CHARON = "Charon"
    KORE = "Kore"
    FENRIR = "Fenrir"
    AOEDE = "Aoede"


class ProblemCategory(str, Enum):
    """Mental health problem categories."""
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    LONELINESS = "loneliness"
    ACADEMIC_PRESSURE = "academic_pressure"
    RELATIONSHIP_ISSUES = "relationship_issues"
    SELF_ESTEEM = "self_esteem"
    CAREER_CONFUSION = "career_confusion"
    FAMILY_PROBLEMS = "family_problems"
    GENERAL_WELLBEING = "general_wellbeing"


class UserPreferences(BaseModel):
    """User preferences and settings."""
    language: str = "en"
    notification_enabled: bool = True
    voice_enabled: bool = True
    meditation_reminders: bool = False
    journal_reminders: bool = False
    crisis_support_enabled: bool = True
    preferred_voice: VoiceType = VoiceType.PUCK
    mitra_name: str = "Mitra"
    age_group: Optional[AgeGroup] = None
    gender: Optional[Gender] = None


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
    onboarding_completed: bool = False


class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    preferences: Optional[UserPreferences] = None


class OnboardingRequest(BaseModel):
    """Request model for completing user onboarding."""
    mitra_name: str = Field(..., min_length=1, max_length=50, description="Personalized name for Mitra")
    age_group: AgeGroup
    gender: Gender
    preferred_voice: VoiceType


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
    onboarding_completed: bool
    is_anonymous: bool
    status: UserStatus
    created_at: datetime
    last_login: datetime
    preferences: UserPreferences
    total_sessions: int
    last_mood_entry: Optional[datetime] = None