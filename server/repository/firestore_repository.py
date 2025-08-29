"""
Repository layer for Firestore database operations.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
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
            # Get current user document
            user = await self.firebase_service.get_user_document(uid)
            if not user:
                logger.error(f"User {uid} not found for session increment")
                return False
            
            # Increment sessions and update last login
            updates = {
                "total_sessions": user.total_sessions + 1,
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
            # Convert datetime objects to ISO format strings for Firestore
            session_data["created_at"] = session.created_at
            session_data["updated_at"] = session.updated_at
            
            # Convert message timestamps to ISO format
            for message in session_data.get("messages", []):
                if "timestamp" in message and isinstance(message["timestamp"], datetime):
                    message["timestamp"] = message["timestamp"]
            
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
                # Convert timestamp strings back to datetime objects if needed
                if "created_at" in session_data and isinstance(session_data["created_at"], str):
                    session_data["created_at"] = datetime.fromisoformat(session_data["created_at"])
                if "updated_at" in session_data and isinstance(session_data["updated_at"], str):
                    session_data["updated_at"] = datetime.fromisoformat(session_data["updated_at"])
                
                # Convert message timestamps
                for message in session_data.get("messages", []):
                    if "timestamp" in message and isinstance(message["timestamp"], str):
                        message["timestamp"] = datetime.fromisoformat(message["timestamp"])
                
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
                logger.error(f"Chat session {session_id} not found for user {uid}")
                return False
            
            # Add message and update metadata
            session.messages.append(message)
            session.total_messages += 1
            session.updated_at = datetime.utcnow()
            
            # Save updated session
            session_data = session.dict()
            session_data["created_at"] = session.created_at
            session_data["updated_at"] = session.updated_at
            
            # Ensure message timestamps are preserved
            for msg in session_data.get("messages", []):
                if "timestamp" in msg and isinstance(msg["timestamp"], datetime):
                    msg["timestamp"] = msg["timestamp"]
            
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
                logger.error(f"Chat session {session_id} not found for user {uid}")
                return False
            
            session.context_summary = summary
            session.updated_at = datetime.utcnow()
            
            session_data = session.dict()
            session_data["created_at"] = session.created_at
            session_data["updated_at"] = session.updated_at
            
            return await self.firebase_service.save_chat_session(uid, session_data)
        except Exception as e:
            logger.error(f"Error updating session summary: {e}")
            return False

    async def update_chat_session(self, session: ChatSession) -> bool:
        """Update an entire chat session."""
        try:
            session_data = session.dict()
            session_data["created_at"] = session.created_at
            session_data["updated_at"] = session.updated_at
            
            # Ensure message timestamps are preserved
            for msg in session_data.get("messages", []):
                if "timestamp" in msg and isinstance(msg["timestamp"], datetime):
                    msg["timestamp"] = msg["timestamp"]
            
            return await self.firebase_service.save_chat_session(session.user_id, session_data)
        except Exception as e:
            logger.error(f"Error updating chat session: {e}")
            return False

    # Mood tracking operations
    async def create_mood_entry(self, mood_entry: MoodEntry) -> bool:
        """Create a new mood entry."""
        try:
            mood_data = mood_entry.dict()
            # Convert date and datetime objects for Firestore storage
            mood_data["date"] = mood_entry.date
            mood_data["created_at"] = mood_entry.created_at
            mood_data["updated_at"] = mood_entry.updated_at
            
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
                # Handle different date formats that might come from Firestore
                if "date" in entry_data:
                    if isinstance(entry_data["date"], str):
                        entry_data["date"] = datetime.fromisoformat(entry_data["date"]).date()
                    elif hasattr(entry_data["date"], 'date'):  # Firestore timestamp
                        entry_data["date"] = entry_data["date"].date()
                
                # Handle datetime conversions
                for field in ["created_at", "updated_at"]:
                    if field in entry_data:
                        if isinstance(entry_data[field], str):
                            entry_data[field] = datetime.fromisoformat(entry_data[field])
                        elif hasattr(entry_data[field], 'timestamp'):  # Firestore timestamp
                            entry_data[field] = entry_data[field].to_datetime()
                
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
            mood_data["date"] = mood_entry.date
            mood_data["created_at"] = mood_entry.created_at
            mood_data["updated_at"] = mood_entry.updated_at
            
            return await self.firebase_service.save_mood_entry(uid, mood_data)
        except Exception as e:
            logger.error(f"Error updating mood entry: {e}")
            return False

    # Journal operations
    async def create_journal_entry(self, journal_entry: JournalEntry) -> bool:
        """Create a new journal entry."""
        try:
            journal_data = journal_entry.model_dump()
            # Store datetime objects directly for Firestore
            journal_data["created_at"] = journal_entry.created_at
            journal_data["updated_at"] = journal_entry.updated_at
            
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
                # Handle datetime conversions from Firestore
                for field in ["created_at", "updated_at"]:
                    if field in entry_data:
                        if isinstance(entry_data[field], str):
                            entry_data[field] = datetime.fromisoformat(entry_data[field])
                        elif hasattr(entry_data[field], 'timestamp'):  # Firestore timestamp
                            entry_data[field] = entry_data[field].to_datetime()
                
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
            journal_data["created_at"] = journal_entry.created_at
            journal_data["updated_at"] = journal_entry.updated_at
            
            return await self.firebase_service.save_journal_entry(uid, journal_data)
        except Exception as e:
            logger.error(f"Error updating journal entry: {e}")
            return False

    # Meditation operations
    async def create_meditation_session(self, meditation: MeditationSession) -> bool:
        """Create a new meditation session."""
        try:
            meditation_data = meditation.dict()
            # Store datetime objects directly for Firestore
            meditation_data["created_at"] = meditation.created_at
            if meditation.completed_at:
                meditation_data["completed_at"] = meditation.completed_at
            
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
            # Get the meditation session first to update it
            # This would normally be a more efficient update operation
            completed_at = datetime.utcnow()
            
            # Use batch write to update the meditation session document
            operations = [{
                'type': 'update',
                'collection': f'users/{uid}/meditation_sessions',
                'document': session_id,
                'data': {
                    'completed': True,
                    'completed_at': completed_at,
                    'mood_after': mood_after
                }
            }]
            
            result = await self.firebase_service.batch_write(operations)
            if result:
                logger.info(f"Completed meditation session {session_id} for user {uid}")
            return result
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
            # Get all user collection data efficiently
            user_data = await self.firebase_service.get_user_collections_data(uid)
            
            # Calculate stats from the collected data
            stats = {
                "total_chat_sessions": len(user_data.get("chat_sessions", [])),
                "total_mood_entries": len(user_data.get("mood_entries", [])),
                "total_journal_entries": len(user_data.get("journal_entries", [])),
                "total_meditation_sessions": len(user_data.get("meditation_sessions", [])),
                "current_streak": 0,  # Would need more complex calculation
                "last_activity": None
            }
            
            # Find most recent activity
            all_activities = []
            
            # Add chat session timestamps
            for session in user_data.get("chat_sessions", []):
                if "updated_at" in session:
                    timestamp = session["updated_at"]
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)
                    elif hasattr(timestamp, 'to_datetime'):
                        timestamp = timestamp.to_datetime()
                    all_activities.append(timestamp)
            
            # Add mood entry timestamps
            for entry in user_data.get("mood_entries", []):
                if "created_at" in entry:
                    timestamp = entry["created_at"]
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)
                    elif hasattr(timestamp, 'to_datetime'):
                        timestamp = timestamp.to_datetime()
                    all_activities.append(timestamp)
            
            # Add journal entry timestamps
            for entry in user_data.get("journal_entries", []):
                if "created_at" in entry:
                    timestamp = entry["created_at"]
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)
                    elif hasattr(timestamp, 'to_datetime'):
                        timestamp = timestamp.to_datetime()
                    all_activities.append(timestamp)
            
            # Add meditation session timestamps
            for session in user_data.get("meditation_sessions", []):
                if "created_at" in session:
                    timestamp = session["created_at"]
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)
                    elif hasattr(timestamp, 'to_datetime'):
                        timestamp = timestamp.to_datetime()
                    all_activities.append(timestamp)
            
            if all_activities:
                stats["last_activity"] = max(all_activities)
            
            # Calculate mood streak (simplified version)
            mood_entries = user_data.get("mood_entries", [])
            if mood_entries:
                # Sort by date descending
                sorted_entries = sorted(
                    mood_entries,
                    key=lambda x: x.get("date", ""),
                    reverse=True
                )
                
                # Simple streak calculation - consecutive days with mood entries
                current_streak = 0
                current_date = date.today()
                
                for entry in sorted_entries:
                    entry_date = entry.get("date")
                    if isinstance(entry_date, str):
                        entry_date = datetime.fromisoformat(entry_date).date()
                    elif hasattr(entry_date, 'date'):
                        entry_date = entry_date.date()
                    
                    if entry_date == current_date:
                        current_streak += 1
                        current_date -= timedelta(days=1)
                    else:
                        break
                
                stats["current_streak"] = current_streak
            
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_chat_sessions": 0,
                "total_mood_entries": 0,
                "total_journal_entries": 0,
                "total_meditation_sessions": 0,
                "current_streak": 0,
                "last_activity": None
            }

    async def cleanup_old_sessions(self, uid: str, days_old: int = 30) -> bool:
        """Clean up old chat sessions for a user."""
        try:
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Get all chat sessions for the user
            user_data = await self.firebase_service.get_user_collections_data(uid)
            chat_sessions = user_data.get("chat_sessions", [])
            
            # Find sessions to delete
            sessions_to_delete = []
            for session in chat_sessions:
                session_date = session.get("created_at")
                if isinstance(session_date, str):
                    session_date = datetime.fromisoformat(session_date)
                elif hasattr(session_date, 'to_datetime'):
                    session_date = session_date.to_datetime()
                
                if session_date and session_date < cutoff_date:
                    sessions_to_delete.append(session.get("session_id"))
            
            if not sessions_to_delete:
                logger.info(f"No old sessions to cleanup for user {uid}")
                return True
            
            # Create batch delete operations
            operations = []
            for session_id in sessions_to_delete:
                operations.append({
                    'type': 'delete',
                    'collection': f'users/{uid}/chat_sessions',
                    'document': session_id
                })
            
            # Execute batch delete
            result = await self.firebase_service.batch_write(operations)
            if result:
                logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions for user {uid}")
            
            return result
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return False

    async def get_chat_sessions_for_user(self, uid: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent chat sessions for a user."""
        try:
            user_data = await self.firebase_service.get_user_collections_data(uid)
            chat_sessions = user_data.get("chat_sessions", [])
            
            # Sort by updated_at descending and limit
            sorted_sessions = sorted(
                chat_sessions,
                key=lambda x: x.get("updated_at", ""),
                reverse=True
            )[:limit]
            
            # Convert timestamps if needed
            for session in sorted_sessions:
                for field in ["created_at", "updated_at"]:
                    if field in session and isinstance(session[field], str):
                        session[field] = datetime.fromisoformat(session[field])
                    elif field in session and hasattr(session[field], 'to_datetime'):
                        session[field] = session[field].to_datetime()
            
            return sorted_sessions
        except Exception as e:
            logger.error(f"Error getting chat sessions for user: {e}")
            return []

    async def delete_chat_session(self, uid: str, session_id: str) -> bool:
        """Delete a specific chat session."""
        try:
            operations = [{
                'type': 'delete',
                'collection': f'users/{uid}/chat_sessions',
                'document': session_id
            }]
            
            result = await self.firebase_service.batch_write(operations)
            if result:
                logger.info(f"Deleted chat session {session_id} for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error deleting chat session: {e}")
            return False

    async def delete_mood_entry(self, uid: str, entry_id: str) -> bool:
        """Delete a specific mood entry."""
        try:
            operations = [{
                'type': 'delete',
                'collection': f'users/{uid}/mood_entries',
                'document': entry_id
            }]
            
            result = await self.firebase_service.batch_write(operations)
            if result:
                logger.info(f"Deleted mood entry {entry_id} for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error deleting mood entry: {e}")
            return False

    async def delete_journal_entry(self, uid: str, entry_id: str) -> bool:
        """Delete a specific journal entry."""
        try:
            operations = [{
                'type': 'delete',
                'collection': f'users/{uid}/journal_entries',
                'document': entry_id
            }]
            
            result = await self.firebase_service.batch_write(operations)
            if result:
                logger.info(f"Deleted journal entry {entry_id} for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error deleting journal entry: {e}")
            return False

    async def get_meditation_sessions_for_user(self, uid: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent meditation sessions for a user."""
        try:
            user_data = await self.firebase_service.get_user_collections_data(uid)
            meditation_sessions = user_data.get("meditation_sessions", [])
            
            # Sort by created_at descending and limit
            sorted_sessions = sorted(
                meditation_sessions,
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )[:limit]
            
            # Convert timestamps if needed
            for session in sorted_sessions:
                for field in ["created_at", "completed_at"]:
                    if field in session and isinstance(session[field], str):
                        session[field] = datetime.fromisoformat(session[field])
                    elif field in session and hasattr(session[field], 'to_datetime'):
                        session[field] = session[field].to_datetime()
            
            return sorted_sessions
        except Exception as e:
            logger.error(f"Error getting meditation sessions for user: {e}")
            return []

    async def delete_user_completely(self, uid: str) -> bool:
        """Delete all user data (for GDPR compliance)."""
        try:
            result = await self.firebase_service.delete_user_data(uid)
            if result:
                logger.info(f"Completely deleted all data for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error deleting user data completely: {e}")
            return False

    async def backup_user_data(self, uid: str) -> Optional[Dict[str, Any]]:
        """Create a backup of all user data."""
        try:
            # Get user profile
            user_profile = await self.get_user(uid)
            if not user_profile:
                return None
            
            # Get all collections data
            collections_data = await self.firebase_service.get_user_collections_data(uid)
            
            backup_data = {
                "user_profile": user_profile.dict(),
                "collections": collections_data,
                "backup_timestamp": datetime.utcnow(),
                "backup_version": "1.0"
            }
            
            logger.info(f"Created backup for user {uid}")
            return backup_data
        except Exception as e:
            logger.error(f"Error creating user backup: {e}")
            return None