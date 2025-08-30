"""
Live voice conversation service using Gemini Live API.
Handles real-time voice conversations with WebSocket connections.
"""

import asyncio
import logging
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
import base64

from google import genai
from google.genai import types

from .base_gemini_service import BaseGeminiService
from core.config import settings
from models.user import UserProfile, ProblemCategory, VoiceOption
from models.wellness import VoiceSession, VoiceSessionState, VoiceTranscriptEvent, VoiceInterruptionEvent

logger = logging.getLogger(__name__)


class LiveVoiceService(BaseGeminiService):
    """Service for managing Live API voice conversations."""

    def __init__(self):
        """Initialize Live Voice service."""
        super().__init__()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def create_voice_session(
        self,
        user_id: str,
        user_profile: Optional[UserProfile] = None,
        problem_category: Optional[ProblemCategory] = None,
        voice_option: str = "Puck",
        language: str = "en"
    ) -> VoiceSession:
        """
        Create a new voice session.

        Args:
            user_id: User ID
            user_profile: User profile for personalization
            problem_category: Problem category for context
            voice_option: Voice preference
            language: Language code

        Returns:
            VoiceSession object
        """
        try:
            session_id = str(uuid.uuid4())

            # Determine voice from user preferences or parameter
            if user_profile and user_profile.preferences:
                voice_option = user_profile.preferences.preferred_voice.value
                language = user_profile.preferences.language

            # Create voice session
            voice_session = VoiceSession(
                session_id=session_id,
                user_id=user_id,
                problem_category=problem_category,
                state=VoiceSessionState.CONNECTING,
                voice_option=voice_option,
                language=language,
                created_at=datetime.utcnow()
            )

            # Store session info for WebSocket handling
            self.active_sessions[session_id] = {
                "session": voice_session,
                "user_profile": user_profile,
                "live_session": None,
                "websocket": None,
                "transcript": []
            }

            logger.info(f"Created voice session {session_id} for user {user_id}")
            return voice_session

        except Exception as e:
            logger.error(f"Error creating voice session: {e}")
            raise

    async def start_live_conversation(
        self,
        session_id: str,
        websocket
    ) -> bool:
        """
        Start the Live API conversation.

        Args:
            session_id: Voice session ID
            websocket: WebSocket connection

        Returns:
            True if started successfully
        """
        try:
            if session_id not in self.active_sessions:
                logger.error(f"Voice session {session_id} not found")
                return False

            session_data = self.active_sessions[session_id]
            voice_session = session_data["session"]
            user_profile = session_data["user_profile"]

            # Configure Live API session
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {"prebuilt_voice_config": {"voice_name": voice_session.voice_option}},
                    "language_config": {"language_code": voice_session.language}
                },
                "input_audio_transcription": {},
                "output_audio_transcription": {},
                "realtime_input_config": {
                    "automatic_activity_detection": {
                        "disabled": False,
                        "start_of_speech_sensitivity": types.StartSensitivity.START_SENSITIVITY_MEDIUM,
                        "end_of_speech_sensitivity": types.EndSensitivity.END_SENSITIVITY_MEDIUM,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 1000,
                    }
                }
            }

            # Add personalized system instruction
            if user_profile:
                system_instruction = self.get_personalized_system_instruction(
                    user_profile,
                    voice_session.problem_category
                )
                if system_instruction:
                    config["system_instruction"] = system_instruction

            # Connect to Gemini Live API
            live_session = self.client.aio.live.connect(
                model=settings.gemini_live_model,
                config=config
            )

            # Store live session and websocket
            session_data["live_session"] = live_session
            session_data["websocket"] = websocket

            # Update session state
            voice_session.state = VoiceSessionState.CONNECTED
            voice_session.connected_at = datetime.utcnow()

            # Start handling Live API messages
            asyncio.create_task(self._handle_live_session(session_id))

            # Send initial greeting if problem category is set
            if voice_session.problem_category:
                mitra_name = user_profile.preferences.mitra_name if user_profile else "Mitra"
                greeting = self._get_initial_greeting(voice_session.problem_category, mitra_name)
                if greeting:
                    await self._send_initial_message(session_id, greeting)

            logger.info(f"Started Live API conversation for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error starting live conversation: {e}")
            await self._update_session_state(session_id, VoiceSessionState.ERROR)
            return False

    async def _handle_live_session(self, session_id: str):
        """
        Handle Live API session messages.

        Args:
            session_id: Voice session ID
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            live_session = session_data["live_session"]
            websocket = session_data["websocket"]

            async with live_session as session:
                async for message in session.receive():
                    await self._process_live_message(session_id, message)

        except Exception as e:
            logger.error(f"Error handling live session {session_id}: {e}")
            await self._update_session_state(session_id, VoiceSessionState.ERROR)

    async def _process_live_message(self, session_id: str, message):
        """
        Process a message from the Live API.

        Args:
            session_id: Voice session ID
            message: Live API message
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            websocket = session_data["websocket"]

            # Handle different message types
            if hasattr(message, 'server_content'):
                server_content = message.server_content

                # Handle interruptions
                if hasattr(server_content, 'interrupted') and server_content.interrupted:
                    await self._handle_interruption(session_id)

                # Handle audio output
                if hasattr(server_content, 'model_turn') and server_content.model_turn:
                    for part in server_content.model_turn.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # Send audio data to client
                            await websocket.send_json({
                                "type": "audio",
                                "data": base64.b64encode(part.inline_data.data).decode(),
                                "timestamp": datetime.utcnow().isoformat()
                            })

                # Handle input transcription
                if hasattr(server_content, 'input_transcription'):
                    transcript_text = server_content.input_transcription.text
                    await self._handle_transcript(session_id, "user", transcript_text)

                # Handle output transcription
                if hasattr(server_content, 'output_transcription'):
                    transcript_text = server_content.output_transcription.text
                    await self._handle_transcript(session_id, "assistant", transcript_text)

            # Handle token usage
            if hasattr(message, 'usage_metadata') and message.usage_metadata:
                await websocket.send_json({
                    "type": "usage",
                    "data": {
                        "total_tokens": message.usage_metadata.total_token_count
                    }
                })

        except Exception as e:
            logger.error(f"Error processing live message for session {session_id}: {e}")

    async def _handle_transcript(self, session_id: str, role: str, text: str):
        """
        Handle transcript updates.

        Args:
            session_id: Voice session ID
            role: Speaker role (user/assistant)
            text: Transcript text
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            websocket = session_data["websocket"]
            timestamp = datetime.utcnow()

            # Add to session transcript
            transcript_entry = {
                "role": role,
                "text": text,
                "timestamp": timestamp.isoformat()
            }
            session_data["transcript"].append(transcript_entry)

            # Send transcript to client
            await websocket.send_json({
                "type": "transcript",
                "data": transcript_entry
            })

            # Update session state based on role
            if role == "user":
                await self._update_session_state(session_id, VoiceSessionState.PROCESSING)
            elif role == "assistant":
                await self._update_session_state(session_id, VoiceSessionState.LISTENING)

            logger.debug(f"Transcript - {role}: {text[:50]}...")

        except Exception as e:
            logger.error(f"Error handling transcript: {e}")

    async def _handle_interruption(self, session_id: str):
        """
        Handle voice interruption.

        Args:
            session_id: Voice session ID
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            websocket = session_data["websocket"]

            # Send interruption event to client
            await websocket.send_json({
                "type": "interruption",
                "data": {
                    "session_id": session_id,
                    "interrupted_at": datetime.utcnow().isoformat(),
                    "reason": "user_speech_detected"
                }
            })

            await self._update_session_state(session_id, VoiceSessionState.LISTENING)
            logger.debug(f"Voice interrupted for session {session_id}")

        except Exception as e:
            logger.error(f"Error handling interruption: {e}")

    async def send_audio_input(self, session_id: str, audio_data: bytes):
        """
        Send audio input to the Live API session.

        Args:
            session_id: Voice session ID
            audio_data: PCM audio data
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data or not session_data["live_session"]:
                logger.error(f"No active live session for {session_id}")
                return

            # Create audio blob
            audio_blob = types.Blob(
                mime_type="audio/pcm;rate=16000",
                data=audio_data
            )

            # Send to Live API
            await session_data["live_session"].send_realtime_input(audio=audio_blob)
            await self._update_session_state(session_id, VoiceSessionState.TALKING)

        except Exception as e:
            logger.error(f"Error sending audio input: {e}")

    async def end_voice_session(self, session_id: str):
        """
        End a voice session.

        Args:
            session_id: Voice session ID
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            # Calculate duration
            voice_session = session_data["session"]
            if voice_session.connected_at:
                duration = (datetime.utcnow() - voice_session.connected_at).total_seconds()
                voice_session.total_duration_seconds = int(duration)

            # Update session
            voice_session.state = VoiceSessionState.ENDED
            voice_session.ended_at = datetime.utcnow()
            voice_session.transcript = session_data["transcript"]

            # Close live session if active
            if session_data["live_session"]:
                try:
                    await session_data["live_session"].__aexit__(None, None, None)
                except:
                    pass

            # Remove from active sessions
            del self.active_sessions[session_id]

            logger.info(f"Ended voice session {session_id}")

        except Exception as e:
            logger.error(f"Error ending voice session: {e}")

    async def _update_session_state(self, session_id: str, new_state: VoiceSessionState):
        """
        Update session state and notify client.

        Args:
            session_id: Voice session ID
            new_state: New session state
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            voice_session = session_data["session"]
            websocket = session_data["websocket"]

            # Update state
            voice_session.state = new_state

            # Send state update to client
            await websocket.send_json({
                "type": "state",
                "data": {
                    "session_id": session_id,
                    "state": new_state.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })

        except Exception as e:
            logger.error(f"Error updating session state: {e}")

    async def _send_initial_message(self, session_id: str, message: str):
        """
        Send initial greeting message.

        Args:
            session_id: Voice session ID
            message: Initial message text
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data or not session_data["live_session"]:
                return

            # Send initial message to Live API
            await session_data["live_session"].send_client_content(
                turns=[{"role": "user", "parts": [{"text": message}]}],
                turn_complete=True
            )

        except Exception as e:
            logger.error(f"Error sending initial message: {e}")

    def _get_initial_greeting(self, problem_category: ProblemCategory, mitra_name: str) -> str:
        """
        Get initial greeting based on problem category.

        Args:
            problem_category: Problem category
            mitra_name: Mitra's name

        Returns:
            Initial greeting message
        """
        greetings = {
            ProblemCategory.STRESS_ANXIETY: f"Hi, I'm {mitra_name}. I understand you're dealing with stress and anxiety. I'm here to listen and help you feel more at ease. How are you feeling right now?",
            ProblemCategory.DEPRESSION_SADNESS: f"Hello, I'm {mitra_name}. I know things might feel heavy right now, and I want you to know that you're not alone. I'm here to support you. Would you like to share what's on your mind?",
            ProblemCategory.RELATIONSHIP_ISSUES: f"Hi there, I'm {mitra_name}. Relationships can be complicated, and it's completely normal to need someone to talk through things with. I'm here to listen without judgment. What's been troubling you?",
            ProblemCategory.ACADEMIC_PRESSURE: f"Hello, I'm {mitra_name}. I understand that academic pressure can feel overwhelming. You're doing your best, and that's what matters. Tell me what's been on your mind lately.",
            ProblemCategory.GENERAL_WELLNESS: f"Hi, I'm {mitra_name}, your AI companion for mental wellness. I'm here to support you on your journey toward better mental health. What would you like to talk about today?"
        }

        return greetings.get(problem_category, greetings[ProblemCategory.GENERAL_WELLNESS])

    def get_session_info(self, session_id: str) -> Optional[VoiceSession]:
        """
        Get voice session information.

        Args:
            session_id: Voice session ID

        Returns:
            VoiceSession object or None
        """
        session_data = self.active_sessions.get(session_id)
        return session_data["session"] if session_data else None

    def get_active_sessions_count(self) -> int:
        """Get count of active voice sessions."""
        return len(self.active_sessions)
