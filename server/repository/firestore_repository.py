"""
Repository layer for Firestore database operations.
This is a legacy wrapper that delegates to specialized repositories for backward compatibility.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from repository.user_repository import UserRepository
from repository.chat_repository import ChatRepository
from repository.wellness_repository import WellnessRepository
from models.user import UserProfile, UserPreferences
from models.chat import ChatSession, ChatMessage
from models.wellness import MoodEntry, JournalEntry, MeditationSession

logger = logging.getLogger(__name__)


class FirestoreRepository:
    """Legacy repository that delegates to specialized repositories for backward compatibility."""
    
    def __init__(self):
        """Initialize repository with specialized sub-repositories."""
        self.user_repo = UserRepository()
        self.chat_repo = ChatRepository()
        self.wellness_repo = WellnessRepository()
        
        # Maintain reference to firebase_service for any direct usage
        self.firebase_service = self.user_repo.firebase_service

    # User operations - delegate to UserRepository
    async def create_user(self, user_profile: UserProfile) -> bool:
        """Create a new user document."""
        return await self.user_repo.create_user(user_profile)

    async def get_user(self, uid: str) -> Optional[UserProfile]:
        """Get user profile by UID."""
        return await self.user_repo.get_user(uid)

    async def update_user(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update user profile."""
        return await self.user_repo.update_user(uid, updates)

    async def update_user_preferences(self, uid: str, preferences: UserPreferences) -> bool:
        """Update user preferences."""
        return await self.user_repo.update_user_preferences(uid, preferences)

    async def increment_user_sessions(self, uid: str) -> bool:
        """Increment user's total session count."""
        return await self.user_repo.increment_user_sessions(uid)

    # Chat operations - delegate to ChatRepository
    async def create_chat_session(self, session: ChatSession) -> bool:
        """Create a new chat session."""
        return await self.chat_repo.create_chat_session(session)

    async def get_chat_session(self, uid: str, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        return await self.chat_repo.get_chat_session(uid, session_id)

    async def add_message_to_session(
        self, 
        uid: str, 
        session_id: str, 
        message: ChatMessage
    ) -> bool:
        """Add a message to an existing chat session."""
        return await self.chat_repo.add_message_to_session(uid, session_id, message)

    async def update_session_summary(
        self, 
        uid: str, 
        session_id: str, 
        summary: str
    ) -> bool:
        """Update session context summary."""
        return await self.chat_repo.update_session_summary(uid, session_id, summary)

    # Mood tracking operations - delegate to WellnessRepository
    async def create_mood_entry(self, mood_entry: MoodEntry) -> bool:
        """Create a new mood entry."""
        return await self.wellness_repo.create_mood_entry(mood_entry)

    async def get_mood_entries(
        self, 
        uid: str, 
        limit: int = 30, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MoodEntry]:
        """Get mood entries for a user within date range."""
        return await self.wellness_repo.get_mood_entries(uid, limit, start_date, end_date)

    async def update_mood_entry(self, uid: str, mood_entry: MoodEntry) -> bool:
        """Update an existing mood entry."""
        return await self.wellness_repo.update_mood_entry(uid, mood_entry)

    # Journal operations - delegate to WellnessRepository
    async def create_journal_entry(self, journal_entry: JournalEntry) -> bool:
        """Create a new journal entry."""
        return await self.wellness_repo.create_journal_entry(journal_entry)

    async def get_journal_entries(self, uid: str, limit: int = 20) -> List[JournalEntry]:
        """Get journal entries for a user."""
        return await self.wellness_repo.get_journal_entries(uid, limit)

    async def update_journal_entry(self, uid: str, journal_entry: JournalEntry) -> bool:
        """Update an existing journal entry."""
        return await self.wellness_repo.update_journal_entry(uid, journal_entry)

    # Meditation operations - delegate to WellnessRepository
    async def create_meditation_session(self, meditation: MeditationSession) -> bool:
        """Create a new meditation session."""
        return await self.wellness_repo.create_meditation_session(meditation)

    async def complete_meditation_session(
        self, 
        uid: str, 
        session_id: str,
        mood_after: Optional[int] = None
    ) -> bool:
        """Mark a meditation session as completed."""
        return await self.wellness_repo.complete_meditation_session(uid, session_id, mood_after)

    # Utility operations
    async def generate_unique_id(self) -> str:
        """Generate a unique ID for new documents."""
        return await self.user_repo.generate_unique_id()

    async def get_user_stats(self, uid: str) -> Dict[str, Any]:
        """Get aggregated stats for a user."""
        return await self.user_repo.get_user_stats(uid)

    async def cleanup_old_sessions(self, uid: str, days_old: int = 30) -> bool:
        """Clean up old chat sessions for a user."""
        return await self.user_repo.cleanup_old_sessions(uid, days_old)

    async def get_chat_sessions_for_user(self, uid: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent chat sessions for a user."""
        return await self.chat_repo.get_chat_sessions_for_user(uid, limit)

    async def delete_chat_session(self, uid: str, session_id: str) -> bool:
        """Delete a specific chat session."""
        return await self.chat_repo.delete_chat_session(uid, session_id)

    async def delete_mood_entry(self, uid: str, entry_id: str) -> bool:
        """Delete a specific mood entry."""
        return await self.wellness_repo.delete_mood_entry(uid, entry_id)

    async def delete_journal_entry(self, uid: str, entry_id: str) -> bool:
        """Delete a specific journal entry."""
        return await self.wellness_repo.delete_journal_entry(uid, entry_id)

    async def get_meditation_sessions_for_user(self, uid: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent meditation sessions for a user."""
        return await self.wellness_repo.get_meditation_sessions_for_user(uid, limit)

    async def delete_user_completely(self, uid: str) -> bool:
        """Delete all user data (for GDPR compliance)."""
        return await self.user_repo.delete_user_completely(uid)

    async def backup_user_data(self, uid: str) -> Optional[Dict[str, Any]]:
        """Create a backup of all user data."""
        return await self.user_repo.backup_user_data(uid)