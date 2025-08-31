"""
Repository for chat-related Firestore operations.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from models.chat import ChatSession, ChatMessage
from repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ChatRepository(BaseRepository):
    """Repository for chat session and message operations."""

    async def create_chat_session(self, session: ChatSession) -> bool:
        """Create a new chat session."""
        try:
            session_data = session.model_dump()
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
                session_data = self._handle_timestamp_conversion(
                    session_data, 
                    ["created_at", "updated_at"]
                )
                
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
            session_data = session.model_dump()
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
            
            session_data = session.model_dump()
            session_data["created_at"] = session.created_at
            session_data["updated_at"] = session.updated_at
            
            return await self.firebase_service.save_chat_session(uid, session_data)
        except Exception as e:
            logger.error(f"Error updating session summary: {e}")
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
                session = self._handle_timestamp_conversion(
                    session, 
                    ["created_at", "updated_at"]
                )
            
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
            
            result = await self.batch_write(operations)
            if result:
                logger.info(f"Deleted chat session {session_id} for user {uid}")
            return result
        except Exception as e:
            logger.error(f"Error deleting chat session: {e}")
            return False

    def _handle_timestamp_conversion(self, data: Dict[str, Any], fields: list) -> Dict[str, Any]:
        """Handle datetime conversion for Firestore storage/retrieval."""
        converted_data = data.copy()

        for field in fields:
            if field in converted_data:
                timestamp = converted_data[field]
                if isinstance(timestamp, str):
                    try:
                        converted_data[field] = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        converted_data[field] = datetime.fromisoformat(timestamp)
                elif hasattr(timestamp, 'to_datetime'):  # Firestore timestamp
                    converted_data[field] = timestamp.to_datetime()
                elif hasattr(timestamp, 'timestamp'):  # Firestore DatetimeWithNanoseconds
                    converted_data[field] = timestamp.timestamp()
                elif hasattr(timestamp, 'seconds'):  # Firestore Timestamp
                    import datetime as dt
                    converted_data[field] = dt.datetime.fromtimestamp(timestamp.seconds)

        return converted_data
