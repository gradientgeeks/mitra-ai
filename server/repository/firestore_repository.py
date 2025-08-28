"""
Repository layer for Firestore database operations.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid

from services.firebase_service import FirebaseService
from models.user import UserProfile, UserPreferences
from models.chat import ChatSession, ChatMessage
from models.wellness import MoodEntry, JournalEntry, MeditationSession

logger = logging.getLogger(__name__)


class FirestoreRepository:
    """Repository for all Firestore database operations."""
    
    def __init__(self):
        """Initialize repository with Firebase service."""
        self.firebase_service = FirebaseService()

    # User operations
    async def create_user(self, user_profile: UserProfile) -> bool:
        """Create a new user document."""
        try:
            return await self.firebase_service.create_user_document(user_profile)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    async def get_user(self, uid: str) -> Optional[UserProfile]:
        """Get user profile by UID."""
        try:
            return await self.firebase_service.get_user_document(uid)
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def update_user(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update user profile."""
        try:
            # Add updated timestamp
            updates["updated_at"] = datetime.utcnow()
            return await self.firebase_service.update_user_document(uid, updates)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    async def update_user_preferences(self, uid: str, preferences: UserPreferences) -> bool:
        """Update user preferences."""
        try:
            updates = {
                "preferences": preferences.dict(),
                "updated_at": datetime.utcnow()
            }
            return await self.firebase_service.update_user_document(uid, updates)
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False

    async def increment_user_sessions(self, uid: str) -> bool:
        """Increment user's total session count."""
        try:
            # In production, use Firestore increment operation
            # For mock, just update the field
            updates = {
                "total_sessions": 1,  # This would be an increment in production
                "last_login": datetime.utcnow()
            }
            return await self.firebase_service.update_user_document(uid, updates)
        except Exception as e:
            logger.error(f"Error incrementing user sessions: {e}")
            return False

    # Chat operations
    async def create_chat_session(self, session: ChatSession) -> bool:
        """Create a new chat session."""
        try:
            session_data = session.dict()
            session_data["created_at"] = session.created_at.isoformat()
            session_data["updated_at"] = session.updated_at.isoformat()
            
            return await self.firebase_service.save_chat_session(
                session.user_id, 
                session_data
            )
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return False

    async def get_chat_session(self, uid: str, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        try:
            session_data = await self.firebase_service.get_chat_session(uid, session_id)
            if session_data:
                return ChatSession(**session_data)
            return None
        except Exception as e:
            logger.error(f"Error getting chat session: {e}")
            return None

    async def add_message_to_session(
        self, 
        uid: str, 
        session_id: str, 
        message: ChatMessage
    ) -> bool:
        """Add a message to an existing chat session."""
        try:
            # Get current session
            session = await self.get_chat_session(uid, session_id)
            if not session:
                return False
            
            # Add message and update metadata
            session.messages.append(message)
            session.total_messages += 1
            session.updated_at = datetime.utcnow()
            
            # Save updated session
            session_data = session.dict()
            session_data["created_at"] = session.created_at.isoformat()
            session_data["updated_at"] = session.updated_at.isoformat()
            
            return await self.firebase_service.save_chat_session(uid, session_data)
        except Exception as e:
            logger.error(f"Error adding message to session: {e}")
            return False

    async def update_session_summary(
        self, 
        uid: str, 
        session_id: str, 
        summary: str
    ) -> bool:
        """Update session context summary."""
        try:
            session = await self.get_chat_session(uid, session_id)
            if not session:
                return False
            
            session.context_summary = summary
            session.updated_at = datetime.utcnow()
            
            session_data = session.dict()
            session_data["created_at"] = session.created_at.isoformat()
            session_data["updated_at"] = session.updated_at.isoformat()
            
            return await self.firebase_service.save_chat_session(uid, session_data)
        except Exception as e:
            logger.error(f"Error updating session summary: {e}")
            return False

    # Mood tracking operations
    async def create_mood_entry(self, mood_entry: MoodEntry) -> bool:
        """Create a new mood entry."""
        try:
            mood_data = mood_entry.dict()
            mood_data["date"] = mood_entry.date.isoformat()
            mood_data["created_at"] = mood_entry.created_at.isoformat()
            mood_data["updated_at"] = mood_entry.updated_at.isoformat()
            
            return await self.firebase_service.save_mood_entry(
                mood_entry.user_id,
                mood_data
            )
        except Exception as e:
            logger.error(f"Error creating mood entry: {e}")
            return False

    async def get_mood_entries(
        self, 
        uid: str, 
        limit: int = 30, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MoodEntry]:
        """Get mood entries for a user within date range."""
        try:
            entries_data = await self.firebase_service.get_mood_entries(uid, limit)
            
            mood_entries = []
            for entry_data in entries_data:
                # Convert date strings back to date objects
                entry_data["date"] = datetime.fromisoformat(entry_data["date"]).date()
                entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
                entry_data["updated_at"] = datetime.fromisoformat(entry_data["updated_at"])
                
                mood_entries.append(MoodEntry(**entry_data))
            
            # Filter by date range if specified
            if start_date or end_date:
                filtered_entries = []
                for entry in mood_entries:
                    if start_date and entry.date < start_date:
                        continue
                    if end_date and entry.date > end_date:
                        continue
                    filtered_entries.append(entry)
                return filtered_entries
            
            return mood_entries
        except Exception as e:
            logger.error(f"Error getting mood entries: {e}")
            return []

    async def update_mood_entry(self, uid: str, mood_entry: MoodEntry) -> bool:
        """Update an existing mood entry."""
        try:
            mood_entry.updated_at = datetime.utcnow()
            
            mood_data = mood_entry.dict()
            mood_data["date"] = mood_entry.date.isoformat()
            mood_data["created_at"] = mood_entry.created_at.isoformat()
            mood_data["updated_at"] = mood_entry.updated_at.isoformat()
            
            return await self.firebase_service.save_mood_entry(uid, mood_data)
        except Exception as e:
            logger.error(f"Error updating mood entry: {e}")
            return False

    # Journal operations
    async def create_journal_entry(self, journal_entry: JournalEntry) -> bool:
        """Create a new journal entry."""
        try:
            journal_data = journal_entry.dict()
            journal_data["created_at"] = journal_entry.created_at.isoformat()
            journal_data["updated_at"] = journal_entry.updated_at.isoformat()
            
            return await self.firebase_service.save_journal_entry(
                journal_entry.user_id,
                journal_data
            )
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            return False

    async def get_journal_entries(self, uid: str, limit: int = 20) -> List[JournalEntry]:
        """Get journal entries for a user."""
        try:
            entries_data = await self.firebase_service.get_journal_entries(uid, limit)
            
            journal_entries = []
            for entry_data in entries_data:
                # Convert datetime strings back to datetime objects
                entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
                entry_data["updated_at"] = datetime.fromisoformat(entry_data["updated_at"])
                
                journal_entries.append(JournalEntry(**entry_data))
            
            return journal_entries
        except Exception as e:
            logger.error(f"Error getting journal entries: {e}")
            return []

    async def update_journal_entry(self, uid: str, journal_entry: JournalEntry) -> bool:
        """Update an existing journal entry."""
        try:
            journal_entry.updated_at = datetime.utcnow()
            
            journal_data = journal_entry.dict()
            journal_data["created_at"] = journal_entry.created_at.isoformat()
            journal_data["updated_at"] = journal_entry.updated_at.isoformat()
            
            return await self.firebase_service.save_journal_entry(uid, journal_data)
        except Exception as e:
            logger.error(f"Error updating journal entry: {e}")
            return False

    # Meditation operations
    async def create_meditation_session(self, meditation: MeditationSession) -> bool:
        """Create a new meditation session."""
        try:
            meditation_data = meditation.dict()
            meditation_data["created_at"] = meditation.created_at.isoformat()
            if meditation.completed_at:
                meditation_data["completed_at"] = meditation.completed_at.isoformat()
            
            return await self.firebase_service.save_meditation_session(
                meditation.user_id,
                meditation_data
            )
        except Exception as e:
            logger.error(f"Error creating meditation session: {e}")
            return False

    async def complete_meditation_session(
        self, 
        uid: str, 
        session_id: str,
        mood_after: Optional[int] = None
    ) -> bool:
        """Mark a meditation session as completed."""
        try:
            # In production, this would be a proper update operation
            # For now, we'll simulate it
            updates = {
                "completed": True,
                "completed_at": datetime.utcnow().isoformat(),
                "mood_after": mood_after
            }
            
            # This would be a specific meditation session update in production
            logger.info(f"Mock: Completing meditation session {session_id} for user {uid}")
            return True
        except Exception as e:
            logger.error(f"Error completing meditation session: {e}")
            return False

    # Utility operations
    async def generate_unique_id(self) -> str:
        """Generate a unique ID for new documents."""
        return str(uuid.uuid4())

    async def get_user_stats(self, uid: str) -> Dict[str, Any]:
        """Get aggregated stats for a user."""
        try:
            # In production, these would be efficient aggregation queries
            # For now, return mock stats
            return {
                "total_chat_sessions": 0,
                "total_mood_entries": 0,
                "total_journal_entries": 0,
                "total_meditation_sessions": 0,
                "current_streak": 0,
                "last_activity": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}

    async def cleanup_old_sessions(self, uid: str, days_old: int = 30) -> bool:
        """Clean up old chat sessions for a user."""
        try:
            # In production, this would delete sessions older than specified days
            # For now, just log the operation
            logger.info(f"Mock: Cleaning up sessions older than {days_old} days for user {uid}")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return False