"""
Voice processing service for Mitra AI.
Handles voice input/output and Live API interactions.
"""

import asyncio
import logging
from typing import List, Tuple, Optional, Dict

from google.genai import types

from .base_gemini_service import BaseGeminiService
from core.config import settings
from models.chat import ChatMessage
from models.user import UserProfile, VoiceOption, ProblemCategory

logger = logging.getLogger(__name__)


class VoiceService(BaseGeminiService):
    """Service for voice processing and Live API interactions."""

    async def generate_voice_response(
        self,
        messages: List[ChatMessage],
        user_profile: Optional[UserProfile] = None,
        problem_category: Optional[ProblemCategory] = None,
        voice: Optional[str] = None,
        language: str = "en"
    ) -> Tuple[bytes, Optional[str]]:
        """
        Generate personalized voice response using Gemini Live API.
        
        Args:
            messages: Conversation history
            user_profile: User profile for personalization
            problem_category: Current session problem category
            voice: Voice to use (overrides user preference)
            language: Language code
            
        Returns:
            Tuple of (audio_data, transcription)
        """
        try:
            # Determine voice from user preferences or default
            selected_voice = voice
            if not selected_voice and user_profile and user_profile.preferences:
                selected_voice = user_profile.preferences.preferred_voice.value
            if not selected_voice:
                selected_voice = "Puck"
            
            # Get personalized system instruction
            system_instruction = None
            if user_profile:
                system_instruction = self.get_personalized_system_instruction(user_profile, problem_category)
            
            # Convert messages to text format for Live API
            conversation_text = self._convert_messages_to_text(messages)
            
            # Add personalized context if available
            if user_profile and user_profile.preferences and user_profile.preferences.mitra_name:
                mitra_name = user_profile.preferences.mitra_name
                conversation_text = f"[Speaking as {mitra_name}]\n\n{conversation_text}"
            
            # Configure Live API session
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {"name": selected_voice},
                    "language_config": {"language_code": language}
                },
                "output_audio_transcription": {}
            }
            
            # Add system instruction if available
            if system_instruction:
                config["system_instruction"] = system_instruction
            
            # Connect to Live API and generate response
            async with self.client.aio.live.connect(
                model=settings.gemini_live_model,
                config=config
            ) as session:
                # Send conversation history as context
                await session.send_client_content(
                    turns=[{"role": "user", "parts": [{"text": conversation_text}]}],
                    turn_complete=True
                )
                
                # Collect audio response
                audio_chunks = []
                transcription = None
                
                async for message in session.receive():
                    if hasattr(message, 'server_content'):
                        for part in message.server_content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                audio_chunks.append(part.inline_data.data)
                            elif hasattr(part, 'text') and part.text:
                                transcription = part.text
                
                # Combine audio chunks
                audio_data = b''.join(audio_chunks) if audio_chunks else b''
                return audio_data, transcription
                
        except Exception as e:
            logger.error(f"Error generating voice response: {e}")
            raise

    async def process_voice_input(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> str:
        """
        Process voice input and convert to text.
        
        Args:
            audio_data: PCM audio data
            sample_rate: Audio sample rate
            
        Returns:
            Transcribed text
        """
        try:
            # Configure Live API for audio-to-text
            config = {
                "response_modalities": ["TEXT"],
                "input_audio_transcription": {}
            }
            
            async with self.client.aio.live.connect(
                model=settings.gemini_live_model,
                config=config
            ) as session:
                # Send audio data
                mime_type = f"audio/pcm;rate={sample_rate}"
                audio_blob = types.Blob(
                    mime_type=mime_type,
                    data=audio_data
                )
                
                await session.send_client_content(
                    turns=[{"role": "user", "parts": [audio_blob]}],
                    turn_complete=True
                )
                
                # Receive transcription
                transcription = ""
                async for message in session.receive():
                    if hasattr(message, 'server_content'):
                        for part in message.server_content.parts:
                            if hasattr(part, 'text') and part.text:
                                transcription += part.text
                
                return transcription.strip()
                
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            raise

    def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available voices with descriptions.
        
        Returns:
            List of available voices with metadata
        """
        voices = [
            {
                "value": VoiceOption.PUCK.value,
                "label": "Puck",
                "description": "Friendly and energetic voice, good for younger users"
            },
            {
                "value": VoiceOption.CHARON.value,
                "label": "Charon",
                "description": "Calm and reassuring voice, suitable for meditation"
            },
            {
                "value": VoiceOption.KORE.value,
                "label": "Kore",
                "description": "Warm and supportive voice, ideal for counseling"
            },
            {
                "value": VoiceOption.FENRIR.value,
                "label": "Fenrir",
                "description": "Strong and confident voice, good for motivation"
            },
            {
                "value": VoiceOption.AOEDE.value,
                "label": "Aoede",
                "description": "Gentle and soothing voice, perfect for relaxation"
            }
        ]
        return voices

    def validate_voice_preference(self, voice: str) -> bool:
        """
        Validate if the voice preference is supported.
        
        Args:
            voice: Voice name to validate
            
        Returns:
            True if voice is supported, False otherwise
        """
        available_voices = [v["value"] for v in self.get_available_voices()]
        return voice in available_voices

    def get_recommended_voice_for_age(self, age_group: str) -> str:
        """
        Get recommended voice based on age group.
        
        Args:
            age_group: User's age group
            
        Returns:
            Recommended voice name
        """
        recommendations = {
            "teen": VoiceOption.PUCK.value,  # Energetic for teens
            "young_adult": VoiceOption.KORE.value,  # Warm and supportive
            "adult": VoiceOption.CHARON.value,  # Calm and professional
            "mature_adult": VoiceOption.AOEDE.value  # Gentle and wise
        }
        return recommendations.get(age_group, VoiceOption.PUCK.value)