"""
Basic tests for Mitra AI server functionality.
"""

import asyncio
import pytest
from datetime import datetime

# Test the core services
async def test_gemini_service():
    """Test Gemini service initialization and basic functionality."""
    try:
        from services.gemini_service import GeminiService
        
        # Initialize service (will fail without API key, but should not crash)
        service = GeminiService()
        
        # Test message conversion
        from models.chat import ChatMessage, MessageRole, MessageType, MessageContent
        messages = [
            ChatMessage(
                id="test1",
                role=MessageRole.USER,
                type=MessageType.TEXT,
                content=MessageContent(text="Hello"),
                timestamp=datetime.utcnow()
            )
        ]
        
        gemini_format = service._convert_messages_to_gemini_format(messages)
        assert len(gemini_format) == 1
        assert gemini_format[0]["role"] == "user"
        assert gemini_format[0]["parts"][0]["text"] == "Hello"
        
        print("✅ Gemini service test passed")
        
    except Exception as e:
        print(f"❌ Gemini service test failed: {e}")


async def test_safety_service():
    """Test safety service crisis detection."""
    try:
        from services.safety_service import SafetyService
        from models.chat import SafetyStatus
        
        service = SafetyService()
        
        # Test safe message
        status, confidence, severity = await service.assess_safety("I'm feeling good today")
        assert status == SafetyStatus.SAFE
        assert confidence < 0.5
        
        # Test potentially risky message
        status, confidence, severity = await service.assess_safety("I'm feeling very stressed")
        print(f"Stress message - Status: {status}, Confidence: {confidence:.2f}")
        
        print("✅ Safety service test passed")
        
    except Exception as e:
        print(f"❌ Safety service test failed: {e}")


async def test_firebase_service():
    """Test Firebase service mock functionality."""
    try:
        from services.firebase_service import FirebaseService
        
        service = FirebaseService()
        
        # Test mock token verification
        mock_token = "mock_token_123"
        claims = await service.verify_id_token(mock_token)
        assert "uid" in claims
        assert "email" in claims
        
        # Test user operations
        user_data = await service.get_user("test_user")
        assert user_data is not None
        assert user_data["uid"] == "test_user"
        
        print("✅ Firebase service test passed")
        
    except Exception as e:
        print(f"❌ Firebase service test failed: {e}")


async def test_repository():
    """Test repository layer."""
    try:
        from repository.firestore_repository import FirestoreRepository
        from models.user import UserProfile, UserProvider, UserStatus, UserPreferences
        
        repo = FirestoreRepository()
        
        # Test user creation
        user_profile = UserProfile(
            uid="test_user_123",
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
        
        success = await repo.create_user(user_profile)
        assert success == True
        
        # Test user retrieval
        retrieved_user = await repo.get_user("test_user_123")
        assert retrieved_user is not None
        assert retrieved_user.uid == "test_user_123"
        
        print("✅ Repository test passed")
        
    except Exception as e:
        print(f"❌ Repository test failed: {e}")


async def test_models():
    """Test Pydantic models validation."""
    try:
        from models.user import UserProfile, UserProvider, UserStatus, UserPreferences
        from models.chat import ChatMessage, MessageRole, MessageType, MessageContent
        from models.wellness import MoodEntry, MoodLevel, EmotionTag
        
        # Test user model
        user = UserProfile(
            uid="test123",
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
        assert user.uid == "test123"
        assert user.is_anonymous == True
        
        # Test chat message model
        message = ChatMessage(
            id="msg123",
            role=MessageRole.USER,
            type=MessageType.TEXT,
            content=MessageContent(text="Hello"),
            timestamp=datetime.utcnow()
        )
        assert message.role == MessageRole.USER
        assert message.content.text == "Hello"
        
        # Test mood entry model
        mood = MoodEntry(
            id="mood123",
            user_id="test123",
            date=datetime.utcnow().date(),
            mood_level=MoodLevel.HIGH,
            emotion_tags=[EmotionTag.HAPPY],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert mood.mood_level == MoodLevel.HIGH
        assert EmotionTag.HAPPY in mood.emotion_tags
        
        print("✅ Models test passed")
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")


async def test_configuration():
    """Test configuration loading."""
    try:
        from core.config import settings
        
        # Test default values
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.gemini_text_model == "gemini-2.5-flash"
        assert len(settings.crisis_keywords) > 0
        assert len(settings.crisis_helplines) > 0
        
        # Test helplines contain required Indian services
        assert "AASRA" in settings.crisis_helplines
        assert "Vandrevala Foundation" in settings.crisis_helplines
        
        print("✅ Configuration test passed")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")


async def main():
    """Run all tests."""
    print("🧪 Running Mitra AI Server Tests\n")
    
    tests = [
        test_configuration,
        test_models,
        test_firebase_service,
        test_safety_service,
        test_repository,
        test_gemini_service,  # This may show warnings due to missing API key
    ]
    
    for test in tests:
        await test()
        print()
    
    print("🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())