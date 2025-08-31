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
<<<<<<< HEAD
    OnboardingRequest
=======
    OnboardingRequest, AgeGroup, Gender, VoiceOption
>>>>>>> feat/voice
)
from models.common import APIResponse, ErrorResponse, ErrorType
from services.firebase_service import FirebaseService
from services.voice_service import VoiceService
from services.image_service import ImageService
from repository.firestore_repository import FirestoreRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Predefined Mitra companions with their characteristics
PREDEFINED_MITRA_COMPANIONS = {
    "Mitra": {
        "gender": "feminine",
        "description": "A wise and nurturing AI companion with gentle eyes and a warm smile",
        "style": "traditional Indian wisdom meets modern compassion"
    },
    "Sakhi": {
        "gender": "feminine", 
        "description": "A caring friend with a bright, encouraging presence and youthful energy",
        "style": "vibrant and friendly with traditional Indian elements"
    },
    "Suhana": {
        "gender": "feminine",
        "description": "An elegant and graceful companion with serene features and calming aura",
        "style": "sophisticated and peaceful with soft, flowing elements"
    },
    "Priya": {
        "gender": "feminine",
        "description": "A loving and empathetic companion with kind eyes and gentle demeanor",
        "style": "warm and approachable with soft pastels"
    },
    "Ishita": {
        "gender": "feminine", 
        "description": "A creative and inspiring companion with artistic flair and imaginative spirit",
        "style": "artistic and colorful with creative elements"
    },
    "Aryan": {
        "gender": "masculine",
        "description": "A strong and supportive companion with confident bearing and trustworthy presence",
        "style": "modern and reliable with clean, professional look"
    },
    "Kiran": {
        "gender": "masculine",
        "description": "A bright and optimistic companion with energetic presence and encouraging smile",
        "style": "youthful and dynamic with bright, positive colors"
    },
    "Rahul": {
        "gender": "masculine",
        "description": "A mature and understanding companion with wise eyes and patient demeanor",
        "style": "sophisticated and calm with mature, grounded appearance"
    },
    "Dev": {
        "gender": "masculine",
        "description": "A tech-savvy and progressive companion with modern outlook and innovative spirit",
        "style": "contemporary and sleek with futuristic elements"
    }
}

# Dependency injection
def get_firebase_service() -> FirebaseService:
    return FirebaseService()

def get_repository() -> FirestoreRepository:
    return FirestoreRepository()

def get_voice_service() -> VoiceService:
    return VoiceService()

def get_image_service() -> ImageService:
    return ImageService()

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
<<<<<<< HEAD
=======
            age_group=user_profile.age_group,
            birth_year=user_profile.birth_year,
>>>>>>> feat/voice
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
    voice_service: VoiceService = Depends(get_voice_service),
    image_service: ImageService = Depends(get_image_service)
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
        
        # Generate Mitra profile image (only for predefined companions)
        profile_image_url = None
        try:
            # Check if this is a predefined Mitra companion
            if request.mitra_name in PREDEFINED_MITRA_COMPANIONS:
                logger.info(f"Checking for existing profile image for predefined Mitra: {request.mitra_name}")
                
                # Try to get existing image URL from Firebase Storage first
                profile_image_url = await _get_existing_mitra_image_url(request.mitra_name)
                
                if not profile_image_url:
                    # Generate new image for predefined companion
                    logger.info(f"Generating new profile image for predefined Mitra: {request.mitra_name}")
                    
                    companion_info = PREDEFINED_MITRA_COMPANIONS[request.mitra_name]
                    
                    prompt = f"""A {companion_info['description']}, {companion_info['style']}, 
                    digital art portrait, soft lighting, peaceful expression, culturally appropriate for Indian youth, 
                    professional quality for mental wellness app, clean background, warm and trustworthy appearance"""
                    
                    # Generate the image
                    image_data = await image_service.generate_image(prompt, "ai_companion_portrait")
                    
                    if image_data:
                        # Save to Firebase Storage
                        profile_image_url = await _save_mitra_image_to_storage(request.mitra_name, image_data)
                        logger.info(f"Successfully generated and saved profile image for {request.mitra_name}")
                else:
                    logger.info(f"Using existing profile image for {request.mitra_name}")
            else:
                logger.info(f"Custom Mitra name '{request.mitra_name}' - skipping image generation")
                
        except Exception as e:
            logger.warning(f"Failed to generate/retrieve profile image for {request.mitra_name}: {e}")
            # Continue without profile image - it's not critical for onboarding

        # Update preferences with profile image URL if available
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
            mitra_profile_image_url=profile_image_url,
            onboarding_completed=True
        )
        
        # Update user profile with profile image URL
        update_data = {
            "preferences": updated_preferences.model_dump(),
            "age_group": request.age_group.value,
            "birth_year": request.birth_year,
            "onboarding_completed": True,
            "mitra_profile_image_url": profile_image_url,
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
            onboarding_completed=updated_profile.onboarding_completed,
            mitra_profile_image_url=profile_image_url
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
<<<<<<< HEAD
=======
            age_group=user_profile.age_group,
            birth_year=user_profile.birth_year,
>>>>>>> feat/voice
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
            last_mood_entry=updated_profile.last_mood_entry,
            onboarding_completed=updated_profile.onboarding_completed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.post("/complete-onboarding", response_model=UserResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Complete user onboarding with personalization preferences."""
    try:
        # Get current profile
        user_profile = await repository.get_user(current_user)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update preferences with onboarding data
        updated_preferences = user_profile.preferences.model_copy()
        updated_preferences.mitra_name = request.mitra_name
        updated_preferences.age_group = request.age_group
        updated_preferences.gender = request.gender
        updated_preferences.preferred_voice = request.preferred_voice
        
        # Prepare updates
        updates = {
            "preferences": updated_preferences.dict(),
            "onboarding_completed": True
        }
        
        success = await repository.update_user(current_user, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to complete onboarding")
        
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
            last_mood_entry=updated_profile.last_mood_entry,
            onboarding_completed=updated_profile.onboarding_completed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing onboarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete onboarding")


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


@router.post("/admin/generate-mitra-images")
async def generate_predefined_mitra_images(
    image_service: ImageService = Depends(get_image_service)
):
    """
    Admin endpoint to pre-generate profile images for all predefined Mitra companions.
    This should be called during system setup to populate the image library.
    """
    try:
        results = {}
        
        for mitra_name, companion_info in PREDEFINED_MITRA_COMPANIONS.items():
            try:
                logger.info(f"Generating profile image for predefined Mitra: {mitra_name}")
                
                # Check if image already exists
                existing_url = await _get_existing_mitra_image_url(mitra_name)
                if existing_url:
                    results[mitra_name] = {
                        "status": "existing",
                        "url": existing_url,
                        "message": "Image already exists"
                    }
                    continue
                
                # Generate new image
                prompt = f"""A {companion_info['description']}, {companion_info['style']}, 
                digital art portrait, soft lighting, peaceful expression, culturally appropriate for Indian youth, 
                professional quality for mental wellness app, clean background, warm and trustworthy appearance"""
                
                image_data = await image_service.generate_image(prompt, "ai_companion_portrait")
                
                if image_data:
                    # Save to storage
                    image_url = await _save_mitra_image_to_storage(mitra_name, image_data)
                    
                    results[mitra_name] = {
                        "status": "generated",
                        "url": image_url,
                        "message": f"Successfully generated image ({len(image_data)} bytes)"
                    }
                else:
                    results[mitra_name] = {
                        "status": "failed",
                        "url": None,
                        "message": "Image generation failed"
                    }
                    
            except Exception as e:
                logger.error(f"Error generating image for {mitra_name}: {e}")
                results[mitra_name] = {
                    "status": "error",
                    "url": None,
                    "message": f"Error: {str(e)}"
                }
        
        return {
            "message": "Mitra image generation completed",
            "results": results,
            "total_processed": len(PREDEFINED_MITRA_COMPANIONS),
            "successful": len([r for r in results.values() if r["status"] in ["generated", "existing"]])
        }
        
    except Exception as e:
        logger.error(f"Error in batch Mitra image generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Mitra images")


@router.get("/admin/mitra-images")
async def list_mitra_images():
    """
    Admin endpoint to list all existing Mitra profile images in Firebase Storage.
    """
    try:
        firebase_service = FirebaseService()
        
        # List all files in the mitra_profiles directory
        file_paths = await firebase_service.list_files_in_directory("mitra_profiles")
        
        images_info = []
        for file_path in file_paths:
            # Extract Mitra name from file path
            file_name = file_path.split("/")[-1]  # Get filename
            mitra_name = file_name.replace(".jpg", "").replace(".jpeg", "").replace(".png", "").title()
            
            # Get public URL
            public_url = await firebase_service.get_file_public_url(file_path)
            
            images_info.append({
                "mitra_name": mitra_name,
                "file_path": file_path,
                "public_url": public_url,
                "is_predefined": mitra_name in PREDEFINED_MITRA_COMPANIONS
            })
        
        return {
            "message": "Mitra images retrieved successfully",
            "total_images": len(images_info),
            "images": images_info,
            "predefined_companions": list(PREDEFINED_MITRA_COMPANIONS.keys())
        }
        
    except Exception as e:
        logger.error(f"Error listing Mitra images: {e}")
        raise HTTPException(status_code=500, detail="Failed to list Mitra images")


# Helper functions for Mitra profile image management

async def _get_existing_mitra_image_url(mitra_name: str) -> Optional[str]:
    """
    Check if a profile image already exists for a predefined Mitra companion.
    
    Args:
        mitra_name: Name of the predefined Mitra companion
        
    Returns:
        URL of existing image or None if not found
    """
    try:
        firebase_service = FirebaseService()
        file_path = f"mitra_profiles/{mitra_name.lower()}.jpg"
        
        # Check if file exists and get public URL
        public_url = await firebase_service.get_file_public_url(file_path)
        
        if public_url:
            logger.info(f"Found existing image for {mitra_name}: {public_url}")
            return public_url
        else:
            logger.debug(f"No existing image found for {mitra_name}")
            return None
        
    except Exception as e:
        logger.error(f"Error checking for existing Mitra image {mitra_name}: {e}")
        return None


async def _save_mitra_image_to_storage(mitra_name: str, image_data: bytes) -> Optional[str]:
    """
    Save a generated Mitra profile image to Firebase Storage.
    
    Args:
        mitra_name: Name of the predefined Mitra companion
        image_data: Generated image data as bytes
        
    Returns:
        URL of saved image or None if failed
    """
    try:
        firebase_service = FirebaseService()
        file_path = f"mitra_profiles/{mitra_name.lower()}.jpg"
        
        # Prepare metadata
        metadata = {
            "mitra_name": mitra_name,
            "generated_at": datetime.utcnow().isoformat(),
            "content_type": "image/jpeg",
            "purpose": "ai_companion_profile"
        }
        
        # Upload to Firebase Storage
        public_url = await firebase_service.upload_file_to_storage(
            file_data=image_data,
            file_path=file_path,
            content_type="image/jpeg",
            metadata=metadata
        )
        
        if public_url:
            logger.info(f"Successfully saved profile image for {mitra_name} ({len(image_data)} bytes): {public_url}")
            return public_url
        else:
            logger.error(f"Failed to save profile image for {mitra_name}")
            return None
        
    except Exception as e:
        logger.error(f"Error saving Mitra image {mitra_name}: {e}")
        return None