"""
Voice processing service for Mitra AI.
Handles voice input/output and Live API interactions.
"""

import asyncio
import logging
from typing import List, Tuple, Optional

from google.genai import types

from .base_gemini_service import BaseGeminiService
from core.config import settings
from models.chat import ChatMessage

logger = logging.getLogger(__name__)


class VoiceService(BaseGeminiService):
    """Service for voice processing and Live API interactions."""

    async def generate_voice_response(
        self,
        messages: List[ChatMessage],
        voice: str = "Puck",
        language: str = "en"
    ) -> Tuple[bytes, Optional[str]]:
        """
        Generate voice response using Gemini Live API.
        
        Args:
            messages: Conversation history
            voice: Voice to use for generation
            language: Language code
            
        Returns:
            Tuple of (audio_data, transcription)
        """
        try:
            # Convert messages to text format for Live API
            conversation_text = self._convert_messages_to_text(messages)
            
            # Configure Live API session
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {"name": voice},
                    "language_config": {"language_code": language}
                },
                "output_audio_transcription": {}
            }
            
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