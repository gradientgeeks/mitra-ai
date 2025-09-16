"""
Flashcard generation service for Mitra AI.
Generates flashcards from journal entries for review and reflection.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.wellness import JournalEntry, Flashcard
from services.base_gemini_service import BaseGeminiService
from repository.firestore_repository import FirestoreRepository

logger = logging.getLogger(__name__)


class FlashcardService(BaseGeminiService):
    """Service for generating flashcards from journal entries."""

    def __init__(self, repository: FirestoreRepository = FirestoreRepository()):
        super().__init__()
        self.repository = repository

    async def generate_flashcards_from_journal(
        self,
        journal_entry: JournalEntry
    ) -> List[Flashcard]:
        """
        Generates flashcards from a journal entry using structured output.

        Args:
            journal_entry: The journal entry to process.

        Returns:
            A list of generated Flashcard objects.
        """
        try:
            prompt = self._create_flashcard_prompt(journal_entry)
            schema = {
                "type": "object",
                "properties": {
                    "flashcards": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "front": {"type": "string"},
                                "back": {"type": "string"},
                            },
                            "required": ["front", "back"],
                        },
                    }
                },
                "required": ["flashcards"],
            }

            response = await self.generate_structured_content(prompt, schema)

            flashcards = []
            for card_data in response.get("flashcards", []):
                flashcard = Flashcard(
                    id=f"flashcard_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}",
                    front=card_data["front"],
                    back=card_data["back"],
                    created_at=datetime.utcnow(),
                )
                flashcards.append(flashcard)

            if flashcards:
                await self.repository.save_flashcards(journal_entry.user_id, journal_entry.id, flashcards)

            return flashcards

        except Exception as e:
            logger.error(f"Error generating flashcards for journal {journal_entry.id}: {e}")
            return []

    def _create_flashcard_prompt(self, journal_entry: JournalEntry) -> str:
        """Creates a prompt for generating flashcards from a journal entry."""
        return f"""
Analyze the following journal entry and create a set of flashcards for the user to review.
The flashcards should help the user reflect on their thoughts and feelings, identify patterns, and reinforce positive insights.
Each flashcard should have a 'front' with a question or a key theme, and a 'back' with a summary, a quote from the journal, or a reflective prompt.

Journal Entry Title: "{journal_entry.title}"
Journal Entry Content:
---
{journal_entry.content}
---

Generate 3-5 flashcards based on this entry.
"""
