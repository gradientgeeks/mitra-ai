"""
Repository for wellness-related Firestore operations.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from models.wellness import MoodEntry, JournalEntry, MeditationSession
from repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class WellnessRepository(BaseRepository):
    """Repository for wellness-related operations (mood, journal, meditation)."""

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
                entry_data = self._handle_timestamp_conversion(
                    entry_data, 
                    ["created_at", "updated_at"]
                )
                
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

    async def delete_mood_entry(self, uid: str, entry_id: str) -> bool:
        """Delete a specific mood entry."""
        try:
            operations = [{
                'type': 'delete',
                'collection': f'users/{uid}/mood_entries',
                'document': entry_id
            }]
            
            result = await self.batch_write(operations)
            if result:
                logger.info(f"Deleted mood entry {entry_id} for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error deleting mood entry: {e}")
            return False

    # Journal operations
    async def create_journal_entry(self, journal_entry: JournalEntry) -> bool:
        """Create a new journal entry."""
        try:
            journal_data = journal_entry.dict()
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
                entry_data = self._handle_timestamp_conversion(
                    entry_data, 
                    ["created_at", "updated_at"]
                )
                
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

    async def delete_journal_entry(self, uid: str, entry_id: str) -> bool:
        """Delete a specific journal entry."""
        try:
            operations = [{
                'type': 'delete',
                'collection': f'users/{uid}/journal_entries',
                'document': entry_id
            }]
            
            result = await self.batch_write(operations)
            if result:
                logger.info(f"Deleted journal entry {entry_id} for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error deleting journal entry: {e}")
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
            
            result = await self.batch_write(operations)
            if result:
                logger.info(f"Completed meditation session {session_id} for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error completing meditation session: {e}")
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
                session = self._handle_timestamp_conversion(
                    session, 
                    ["created_at", "completed_at"]
                )
            
            return sorted_sessions
        except Exception as e:
            logger.error(f"Error getting meditation sessions for user: {e}")
            return []

    # Flashcard operations
    async def save_flashcards(self, uid: str, journal_entry_id: str, flashcards: List) -> bool:
        """Save a list of flashcards to a journal entry."""
        try:
            operations = []
            for flashcard in flashcards:
                flashcard_data = flashcard.dict()
                flashcard_data["created_at"] = flashcard.created_at
                operations.append({
                    'type': 'set',
                    'collection': f'users/{uid}/journal_entries/{journal_entry_id}/flashcards',
                    'document': flashcard.id,
                    'data': flashcard_data
                })

            result = await self.batch_write(operations)
            if result:
                logger.info(f"Saved {len(flashcards)} flashcards for journal entry {journal_entry_id}")
            return result
        except Exception as e:
            logger.error(f"Error saving flashcards: {e}")
            return False