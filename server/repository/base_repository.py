"""
Base repository class for common Firestore operations.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository class with common Firestore functionality."""
    
    def __init__(self):
        """Initialize repository with Firebase service."""
        self.firebase_service = FirebaseService()

    async def generate_unique_id(self) -> str:
        """Generate a unique ID for new documents."""
        return str(uuid.uuid4())

    def _handle_timestamp_conversion(self, data: Dict[str, Any], fields: list) -> Dict[str, Any]:
        """Handle datetime conversion for Firestore storage/retrieval."""
        converted_data = data.copy()
        
        for field in fields:
            if field in converted_data:
                timestamp = converted_data[field]
                if isinstance(timestamp, str):
                    converted_data[field] = datetime.fromisoformat(timestamp)
                elif hasattr(timestamp, 'to_datetime'):  # Firestore timestamp
                    converted_data[field] = timestamp.to_datetime()
                elif hasattr(timestamp, 'timestamp'):  # Firestore timestamp
                    converted_data[field] = timestamp.to_datetime()
        
        return converted_data

    def _prepare_for_firestore(self, data: Dict[str, Any], datetime_fields: list = None) -> Dict[str, Any]:
        """Prepare data for Firestore storage by handling datetime objects."""
        if datetime_fields is None:
            datetime_fields = ["created_at", "updated_at"]
        
        prepared_data = data.copy()
        
        for field in datetime_fields:
            if field in prepared_data and isinstance(prepared_data[field], datetime):
                # Keep datetime objects as is for Firestore
                continue
        
        return prepared_data

    async def batch_write(self, operations: list) -> bool:
        """Execute batch write operations."""
        try:
            return await self.firebase_service.batch_write(operations)
        except Exception as e:
            logger.error(f"Error in batch write: {e}")
            return False