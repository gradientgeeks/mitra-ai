"""
User router for authentication and user management.
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Header

from models.user import (
    UserProfile, UserResponse, CreateUserRequest, UpdateUserRequest,
    LinkAccountRequest, UserProvider, UserStatus, UserPreferences,
    OnboardingRequest, AgeGroup, Gender, VoiceOption
)
from models.common import APIResponse, ErrorResponse, ErrorType
from services.firebase_service import FirebaseService
from services.voice_service import VoiceService
from repository.firestore_repository import FirestoreRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
def get_firebase_service() -> FirebaseService:
    return FirebaseService()

def get_repository() -> FirestoreRepository:
    return FirestoreRepository()

def get_voice_service() -> VoiceService:
    return VoiceService()

async def get_current_user_optional(authorization: str = Header(None)) -> Optional[str]:
    """Extract user ID from authorization header (optional)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        firebase_service = FirebaseService()
        token_claims = await firebase_service.verify_id_token(token)
        return token_claims.get("uid")
    except Exception:
        return None

async def get_current_user(authorization: str = Header(None)) -> str:
    """Extract user ID from authorization header (required)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    try:
        token = authorization.split(" ")[1]
        firebase_service = FirebaseService()
        token_claims = await firebase_service.verify_id_token(token)
        user_id = token_claims.get("uid")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token - no user ID found")
        
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authorization token")


@router.post("/create-anonymous", response_model=UserResponse)
async def create_anonymous_user(
    current_user_id: str = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Create anonymous user in backend after Firebase Auth."""
    logger.info(f"Creating anonymous user for Firebase UID: {current_user_id}")
    
    try:
        logger.info(f"Create anonymous user request for: {current_user_id}")
        
        # Check if user already exists
        existing_user = await repository.get_user(current_user_id)
        if existing_user:
            return UserResponse(
                uid=existing_user.uid,
                provider=existing_user.provider,
                email=existing_user.email,
                display_name=existing_user.display_name,
                is_anonymous=existing_user.is_anonymous,
                status=existing_user.status,
                created_at=existing_user.created_at,
                last_login=existing_user.last_login,
                preferences=existing_user.preferences,
                total_sessions=existing_user.total_sessions,
                last_mood_entry=existing_user.last_mood_entry,
                age_group=existing_user.age_group,
                birth_year=existing_user.birth_year,
                onboarding_completed=existing_user.onboarding_completed
            )
        
        # Create user profile with actual Firebase user ID
        user_profile = UserProfile(
            uid=current_user_id,
            provider=UserProvider.ANONYMOUS,
            email=None,
            display_name=None,
            is_anonymous=True,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            preferences=UserPreferences(),
            total_sessions=0,
            last_mood_entry=None
        )
        
        # Save to database
        success = await repository.create_user(user_profile)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return UserResponse(
            uid=user_profile.uid,
            provider=user_profile.provider,
            email=user_profile.email,
            display_name=user_profile.display_name,
            is_anonymous=user_profile.is_anonymous,
            status=user_profile.status,
            created_at=user_profile.created_at,
            last_login=user_profile.last_login,
            preferences=user_profile.preferences,
            total_sessions=user_profile.total_sessions,
            last_mood_entry=user_profile.last_mood_entry,
            age_group=user_profile.age_group,
            birth_year=user_profile.birth_year,
            onboarding_completed=user_profile.onboarding_completed
        )
        
    except Exception as e:
        logger.error(f"Error creating anonymous user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.post("/onboarding", response_model=UserResponse)
async def complete_user_onboarding(
    request: OnboardingRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """Complete user onboarding with personalization."""
    try:
        logger.info(f"Onboarding request received for user {current_user}")
        logger.info(f"Request data: {request.dict()}")
        
        # Get existing user profile
        user_profile = await repository.get_user(current_user)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate voice preference
        if not voice_service.validate_voice_preference(request.preferred_voice.value):
            raise HTTPException(status_code=400, detail="Invalid voice preference")
        
        # Update user preferences with onboarding data
        updated_preferences = UserPreferences(
            language=request.language,
            notification_enabled=request.notification_enabled,
            voice_enabled=True,
            meditation_reminders=request.meditation_reminders,
            journal_reminders=request.journal_reminders,
            crisis_support_enabled=True,
            preferred_voice=request.preferred_voice,
            mitra_name=request.mitra_name,
            mitra_gender=request.mitra_gender,
            age_group=request.age_group,
            onboarding_completed=True
        )
        
        # Update user profile
        update_data = {
            "preferences": updated_preferences.model_dump(),
            "age_group": request.age_group.value,
            "birth_year": request.birth_year,
            "onboarding_completed": True,
            "updated_at": datetime.utcnow()
        }
        
        success = await repository.update_user(current_user, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user profile")
        
        # Get updated user profile
        updated_profile = await repository.get_user(current_user)
        
        return UserResponse(
            uid=updated_profile.uid,
            provider=updated_profile.provider,
            email=updated_profile.email,
            display_name=updated_profile.display_name,
            is_anonymous=updated_profile.is_anonymous,
            status=updated_profile.status,
            created_at=updated_profile.created_at,
            last_login=updated_profile.last_login,
            preferences=updated_profile.preferences,
            total_sessions=updated_profile.total_sessions,
            last_mood_entry=updated_profile.last_mood_entry,
            age_group=updated_profile.age_group,
            birth_year=updated_profile.birth_year,
            onboarding_completed=updated_profile.onboarding_completed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing onboarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete onboarding")


@router.get("/onboarding/options")
async def get_onboarding_options(
    voice_service: VoiceService = Depends(get_voice_service)
):
    """Get available options for user onboarding."""
    try:
        return {
            "age_groups": [
                {"value": age.value, "label": age.value.replace("_", " ").title()}
                for age in AgeGroup
            ],
            "genders": [
                {"value": gender.value, "label": gender.value.replace("_", " ").title()}
                for gender in Gender
            ],
            "voices": voice_service.get_available_voices(),
            "sample_mitra_names": [
                "Mitra", "Sakhi", "Suhana", "Aryan", "Kiran", 
                "Priya", "Rahul", "Ananya", "Dev", "Ishita"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting onboarding options: {e}")
        raise HTTPException(status_code=500, detail="Failed to get onboarding options")


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get current user's profile."""
    try:
        user_profile = await repository.get_user(current_user)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            uid=user_profile.uid,
            provider=user_profile.provider,
            email=user_profile.email,
            display_name=user_profile.display_name,
            is_anonymous=user_profile.is_anonymous,
            status=user_profile.status,
            created_at=user_profile.created_at,
            last_login=user_profile.last_login,
            preferences=user_profile.preferences,
            total_sessions=user_profile.total_sessions,
            last_mood_entry=user_profile.last_mood_entry,
            age_group=user_profile.age_group,
            birth_year=user_profile.birth_year,
            onboarding_completed=user_profile.onboarding_completed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    request: UpdateUserRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Update user profile."""
    try:
        # Get current profile
        user_profile = await repository.get_user(current_user)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare updates
        updates = {}
        
        if request.display_name is not None:
            updates["display_name"] = request.display_name
        
        if request.preferences is not None:
            updates["preferences"] = request.preferences.dict()
        
        if updates:
            success = await repository.update_user(current_user, updates)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update profile")
        
        # Get updated profile
        updated_profile = await repository.get_user(current_user)
        
        return UserResponse(
            uid=updated_profile.uid,
            provider=updated_profile.provider,
            email=updated_profile.email,
            display_name=updated_profile.display_name,
            is_anonymous=updated_profile.is_anonymous,
            status=updated_profile.status,
            created_at=updated_profile.created_at,
            last_login=updated_profile.last_login,
            preferences=updated_profile.preferences,
            total_sessions=updated_profile.total_sessions,
            last_mood_entry=updated_profile.last_mood_entry
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.post("/link-account", response_model=UserResponse)
async def link_account(
    request: LinkAccountRequest,
    current_user: str = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Link anonymous account with permanent authentication provider."""
    try:
        # Verify the ID token
        token_claims = await firebase_service.verify_id_token(request.id_token)
        
        # Get current user profile
        user_profile = await repository.get_user(current_user)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user_profile.is_anonymous:
            raise HTTPException(status_code=400, detail="Account is already linked")
        
        # Update user profile with permanent account info
        updates = {
            "provider": request.provider.value,
            "email": request.email or token_claims.get("email"),
            "is_anonymous": False,
            "last_login": datetime.utcnow()
        }
        
        success = await repository.update_user(current_user, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to link account")
        
        # Get updated profile
        updated_profile = await repository.get_user(current_user)
        
        logger.info(f"Successfully linked account for user {current_user}")
        
        return UserResponse(
            uid=updated_profile.uid,
            provider=updated_profile.provider,
            email=updated_profile.email,
            display_name=updated_profile.display_name,
            is_anonymous=updated_profile.is_anonymous,
            status=updated_profile.status,
            created_at=updated_profile.created_at,
            last_login=updated_profile.last_login,
            preferences=updated_profile.preferences,
            total_sessions=updated_profile.total_sessions,
            last_mood_entry=updated_profile.last_mood_entry
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking account: {e}")
        raise HTTPException(status_code=500, detail="Failed to link account")


@router.post("/signin")
async def sign_in_user(
    id_token: str,
    firebase_service: FirebaseService = Depends(get_firebase_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Sign in user with existing account."""
    try:
        # Verify the ID token
        token_claims = await firebase_service.verify_id_token(id_token)
        user_id = token_claims.get("uid")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get or create user profile
        user_profile = await repository.get_user(user_id)
        
        if not user_profile:
            # Create new user profile for existing Firebase user
            user_profile = UserProfile(
                uid=user_id,
                provider=UserProvider.GOOGLE,  # Determine from token
                email=token_claims.get("email"),
                display_name=token_claims.get("name"),
                is_anonymous=False,
                status=UserStatus.ACTIVE,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                preferences=UserPreferences(),
                total_sessions=0,
                last_mood_entry=None
            )
            
            await repository.create_user(user_profile)
        else:
            # Update last login
            await repository.update_user(user_id, {
                "last_login": datetime.utcnow()
            })
        
        return {
            "message": "Sign in successful",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error signing in user: {e}")
        raise HTTPException(status_code=500, detail="Failed to sign in")


@router.post("/refresh-session")
async def refresh_session(
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Refresh user session and update activity timestamp."""
    try:
        # Update last login and increment session count
        await repository.update_user(current_user, {
            "last_login": datetime.utcnow()
        })
        
        await repository.increment_user_sessions(current_user)
        
        return {"message": "Session refreshed"}
        
    except Exception as e:
        logger.error(f"Error refreshing session: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh session")


@router.delete("/account")
async def delete_user_account(
    current_user: str = Depends(get_current_user),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Delete user account and all associated data."""
    try:
        # In production, this would:
        # 1. Delete all user data from Firestore
        # 2. Delete user from Firebase Auth
        # 3. Clean up any external resources
        
        # For now, just log the operation
        logger.info(f"Mock: Deleting account for user {current_user}")
        
        # Update user status to inactive
        await repository.update_user(current_user, {
            "status": UserStatus.SUSPENDED.value,
            "deleted_at": datetime.utcnow()
        })
        
        return {"message": "Account deletion initiated"}
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get user preferences."""
    try:
        user_profile = await repository.get_user(current_user)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_profile.preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get preferences")


@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Update user preferences."""
    try:
        success = await repository.update_user_preferences(current_user, preferences)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.get("/stats")
async def get_user_stats(
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get user activity statistics."""
    try:
        stats = await repository.get_user_stats(current_user)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user stats")