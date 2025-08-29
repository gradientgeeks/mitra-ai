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
    """Age groups for personalized content."""
    TEEN = "teen"          # 13-17 years
    YOUNG_ADULT = "young_adult"  # 18-24 years
    ADULT = "adult"        # 25-34 years
    MATURE_ADULT = "mature_adult"  # 35+ years


class Gender(str, Enum):
    """Gender options for Mitra personalization."""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class VoiceOption(str, Enum):
    """Available voice options for conversations."""
    PUCK = "Puck"
    CHARON = "Charon"
    KORE = "Kore"
    FENRIR = "Fenrir"
    AOEDE = "Aoede"


class ProblemCategory(str, Enum):
    """Problem categories for targeted support."""
    STRESS_ANXIETY = "stress_anxiety"
    DEPRESSION_SADNESS = "depression_sadness"
    RELATIONSHIP_ISSUES = "relationship_issues"
    ACADEMIC_PRESSURE = "academic_pressure"
    CAREER_CONFUSION = "career_confusion"
    FAMILY_PROBLEMS = "family_problems"
    SOCIAL_ANXIETY = "social_anxiety"
    SELF_ESTEEM = "self_esteem"
    SLEEP_ISSUES = "sleep_issues"
    ANGER_MANAGEMENT = "anger_management"
    ADDICTION_HABITS = "addiction_habits"
    GRIEF_LOSS = "grief_loss"
    IDENTITY_CRISIS = "identity_crisis"
    LONELINESS = "loneliness"
    GENERAL_WELLNESS = "general_wellness"


class UserPreferences(BaseModel):
    """User preferences and settings."""
    language: str = "en"
    notification_enabled: bool = True
    voice_enabled: bool = True
    meditation_reminders: bool = False
    journal_reminders: bool = False
    crisis_support_enabled: bool = True
    preferred_voice: VoiceOption = VoiceOption.PUCK
    mitra_name: str = "Mitra"
    mitra_gender: Gender = Gender.FEMALE
    age_group: Optional[AgeGroup] = None
    onboarding_completed: bool = False


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
    # New onboarding fields
    age_group: Optional[AgeGroup] = None
    birth_year: Optional[int] = Field(None, ge=1950, le=2010)
    onboarding_completed: bool = False
    mitra_profile_image_url: Optional[str] = None


class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    preferences: Optional[UserPreferences] = None


class OnboardingRequest(BaseModel):
    """Request model for user onboarding."""
    age_group: AgeGroup = Field(..., description="User's age group for personalized content")
    birth_year: Optional[int] = Field(None, ge=1950, le=2010, description="Birth year for age verification")
    mitra_name: str = Field("Mitra", min_length=1, max_length=20, description="Personalized name for AI companion")
    mitra_gender: Gender = Field(Gender.FEMALE, description="Gender preference for AI companion")
    preferred_voice: VoiceOption = Field(VoiceOption.PUCK, description="Voice preference for conversations")
    language: str = Field("en", description="Preferred language")
    notification_enabled: bool = Field(True, description="Enable notifications")
    meditation_reminders: bool = Field(False, description="Enable meditation reminders")
    journal_reminders: bool = Field(False, description="Enable journal reminders")


class UpdateUserRequest(BaseModel):
    """Request model for updating user profile."""
    display_name: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    age_group: Optional[AgeGroup] = None
    birth_year: Optional[int] = Field(None, ge=1950, le=2010)


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
    age_group: Optional[AgeGroup] = None
    birth_year: Optional[int] = None
    onboarding_completed: bool = False
    mitra_profile_image_url: Optional[str] = None
