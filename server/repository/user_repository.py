"""
Repository for user-related Firestore operations.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta

from models.user import UserProfile, UserPreferences
from repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for user profile and preferences operations."""

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
            result = await self.batch_write(operations)
            if result:
                logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions for user {uid}")
            
            return result
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return False

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