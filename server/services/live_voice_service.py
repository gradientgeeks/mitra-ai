"""
Live voice conversation service using Gemini Live API.
Handles real-time voice conversations with WebSocket connections for phone call-like experience.
"""

import asyncio
import logging
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
import base64

from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from .base_gemini_service import BaseGeminiService
from core.config import settings
from models.user import UserProfile, ProblemCategory, VoiceOption
from models.wellness import VoiceSession, VoiceSessionState

logger = logging.getLogger(__name__)


class LiveVoiceService(BaseGeminiService):
    """Service for managing Live API voice conversations with phone call-like experience."""

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
        Create a new voice session for phone call-like conversation.
        """
        try:
            session_id = str(uuid.uuid4())
            if user_profile and user_profile.preferences:
                voice_option = user_profile.preferences.preferred_voice.value
                language = user_profile.preferences.language

            voice_session = VoiceSession(
                session_id=session_id,
                user_id=user_id,
                problem_category=problem_category,
                state=VoiceSessionState.CONNECTING,
                voice_option=voice_option,
                language=language,
                created_at=datetime.utcnow()
            )

            self.active_sessions[session_id] = {
                "session": voice_session,
                "user_profile": user_profile,
                "live_session": None,
                "websocket": None,
                "transcript": [],
                "is_speaking": False,
                "conversation_started": False
            }

            logger.info(f"Created voice session {session_id} for user {user_id}")
            return voice_session

        except Exception as e:
            logger.error(f"Error creating voice session: {e}")
            raise

    async def handle_voice_call(self, session_id: str, websocket: WebSocket):
        """
        Manages the entire lifecycle of a voice call, from WebSocket connection
        to Gemini Live API interaction and cleanup.
        """
        if session_id not in self.active_sessions:
            logger.error(f"Voice session {session_id} not found for incoming WebSocket.")
            await websocket.close(code=1008, reason="Session not found")
            return

        session_data = self.active_sessions[session_id]
        session_data["websocket"] = websocket
        voice_session = session_data["session"]
        user_profile = session_data["user_profile"]

        try:
            config = self._get_live_api_config(voice_session)
            system_instruction = self._get_personalized_system_instruction(
                user_profile, voice_session.problem_category
            )

            async with self.client.aio.live.connect(
                model="gemini-live-2.5-flash-preview",
                config=config,
                system_instruction=system_instruction,
            ) as live_session:

                session_data["live_session"] = live_session
                voice_session.state = VoiceSessionState.CONNECTED
                voice_session.connected_at = datetime.utcnow()

                logger.info(f"Live API connected for session {session_id}")

                await websocket.send_json({
                    "type": "connected",
                    "data": {
                        "session_id": session_id,
                        "message": "Voice conversation started",
                        "timestamp": voice_session.connected_at.isoformat()
                    }
                })

                await self._send_initial_greeting(session_id)

                client_listener = asyncio.create_task(self._listen_to_client(websocket, session_id))
                gemini_listener = asyncio.create_task(self._listen_to_gemini(live_session, session_id))

                done, pending = await asyncio.wait(
                    [client_listener, gemini_listener],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in pending:
                    task.cancel()

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {session_id}")
        except Exception as e:
            logger.error(f"Error during voice call for session {session_id}: {e}", exc_info=True)
            await self._send_error_to_client(session_id, "An unexpected server error occurred.")
        finally:
            logger.info(f"Ending voice session {session_id} due to connection closure or error.")
            await self.end_voice_session(session_id)


    async def _listen_to_client(self, websocket: WebSocket, session_id: str):
        """Listens for messages from the WebSocket client and handles them."""
        try:
            while True:
                message = await websocket.receive_json()
                await self._handle_websocket_message(session_id, message)
        except WebSocketDisconnect:
            logger.info(f"Client disconnected for session {session_id}.")
            raise # Propagate to terminate the session
        except Exception as e:
            logger.error(f"Error listening to client for session {session_id}: {e}")
            raise # Propagate to terminate the session

    async def _listen_to_gemini(self, live_session, session_id: str):
        """Listens for messages from the Gemini Live API and processes them."""
        try:
            async for message in live_session.receive():
                await self._process_live_message(session_id, message)
        except Exception as e:
            logger.error(f"Error receiving from Gemini for session {session_id}: {e}")
            raise # Propagate to terminate the session


    def _get_live_api_config(self, voice_session: VoiceSession) -> Dict[str, Any]:
        """Builds the configuration for the Gemini Live API."""
        return {
            "response_modalities": ["AUDIO", "TEXT"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": voice_session.voice_option
                    }
                }
            },
            "input_audio_transcription": {},
            "output_audio_transcription": {},
            "realtime_input_config": {
                "automatic_activity_detection": {
                    "disabled": False,
                    "start_of_speech_sensitivity": types.StartSensitivity.START_SENSITIVITY_HIGH,
                    "end_of_speech_sensitivity": types.EndSensitivity.END_SENSITIVITY_HIGH,
                    "prefix_padding_ms": 200,
                    "silence_duration_ms": 800,
                }
            }
        }

    async def _process_live_message(self, session_id: str, message: Any):
        """Processes a single message from the Gemini Live API."""
        session_data = self.active_sessions.get(session_id)
        if not session_data or not session_data.get("websocket"):
            return

        try:
            if isinstance(message, types.live.Audio):
                await self._send_audio_to_client(session_id, message.audio)
            elif isinstance(message, types.live.Transcript):
                await self._handle_transcript(session_id, "assistant", message.text, is_final=message.is_final)
            elif isinstance(message, types.live.UsageMetadata):
                await self._send_usage_info(session_id, message.usage_metadata)
            else:
                logger.warning(f"Received unknown message type from Gemini: {type(message)}")
        except Exception as e:
            logger.error(f"Error processing live message for session {session_id}: {e}")


    async def _handle_websocket_message(self, session_id: str, message: dict):
        """Handles a single message from the WebSocket client."""
        message_type = message.get("type")
        data = message.get("data", {})

        if message_type == "audio_stream":
            audio_data_b64 = data.get("audio")
            if audio_data_b64:
                audio_data = base64.b64decode(audio_data_b64)
                await self.send_audio_input(session_id, audio_data)
        elif message_type == "end_session":
            await self.end_voice_session(session_id)
        # Add other message type handlers as needed (ping, etc.)


    async def send_audio_input(self, session_id: str, audio_data: bytes):
        """Sends audio input from the client to the Gemini Live API."""
        session_data = self.active_sessions.get(session_id)
        if session_data and session_data.get("live_session"):
            try:
                await session_data["live_session"].send_audio(audio_data)
            except Exception as e:
                logger.error(f"Error sending audio to Gemini for session {session_id}: {e}")

    async def _send_initial_greeting(self, session_id: str):
        """Sends a personalized initial greeting to start the conversation."""
        session_data = self.active_sessions.get(session_id)
        if not session_data or not session_data.get("live_session"):
            return

        user_profile = session_data["user_profile"]
        voice_session = session_data["session"]

        user_name = user_profile.display_name if user_profile else "there"
        mitra_name = (user_profile.preferences.mitra_name if user_profile and
                      user_profile.preferences else "Mitra")

        greeting = self._get_category_specific_greeting(
            voice_session.problem_category, mitra_name
        ) if voice_session.problem_category else (
            f"Hello {user_name}! I'm {mitra_name}, your AI wellness companion. "
            "I'm here to listen and support you. How are you feeling today?"
        )

        try:
            await session_data["live_session"].send_text(greeting)
            session_data["conversation_started"] = True
        except Exception as e:
            logger.error(f"Error sending initial greeting for session {session_id}: {e}")

    def _get_personalized_system_instruction(self, user_profile: Optional[UserProfile], problem_category: Optional[ProblemCategory]) -> str:
        """Get personalized system instruction for the Live API."""
        base_instruction = """You are Mitra, a compassionate AI wellness companion specializing in mental health support. 

IMPORTANT GUIDELINES:
- Respond with natural, conversational audio in a warm, empathetic tone
- Keep responses concise and engaging (30-60 seconds of speech)
- Use active listening techniques and validate emotions
- Ask follow-up questions to encourage deeper sharing
- Provide gentle guidance and coping strategies when appropriate
- Be supportive but not prescriptive - you're not replacing professional therapy
- Use the user's name occasionally to create connection
- Respond as if this is a live phone conversation

CONVERSATION STYLE:
- Natural pauses and conversational flow
- Empathetic acknowledgments ("I hear you", "That sounds difficult")
- Gentle probing questions to understand better
- Offer practical wellness techniques when relevant
- Maintain professional boundaries while being warm and caring"""

        if user_profile:
            user_name = user_profile.display_name or "friend"
            mitra_name = user_profile.preferences.mitra_name if user_profile.preferences else "Mitra"
            base_instruction += f"\n\nUser's name: {user_name}\nYour name is: {mitra_name}"

        if problem_category:
            category_guidance = {
                ProblemCategory.STRESS_ANXIETY: "Focus on breathing techniques, grounding exercises, and anxiety management strategies.",
                ProblemCategory.DEPRESSION_SADNESS: "Emphasize emotional validation, gentle encouragement, and mood improvement techniques.",
                ProblemCategory.RELATIONSHIP_ISSUES: "Focus on communication skills, boundary setting, and relationship dynamics.",
                ProblemCategory.SELF_ESTEEM: "Emphasize self-compassion, strength identification, and confidence building.",
                ProblemCategory.GRIEF_LOSS: "Provide gentle support, validation of grief process, and coping strategies.",
                ProblemCategory.SOCIAL_ANXIETY: "Focus on social confidence building, exposure techniques, and coping strategies.",
                ProblemCategory.GENERAL_WELLNESS: "Be flexible and responsive to whatever the user wants to discuss."
            }

            if problem_category in category_guidance:
                base_instruction += f"\n\nSPECIFIC FOCUS: {category_guidance[problem_category]}"

        return base_instruction

    def _get_category_specific_greeting(self, problem_category: ProblemCategory, mitra_name: str) -> str:
        """Get category-specific greeting."""
        greetings = {
            ProblemCategory.STRESS_ANXIETY: f"Hi there! I'm {mitra_name}. I understand you're dealing with some stress and anxiety right now. That takes courage to reach out. I'm here to listen and help you work through these feelings. Take a deep breath with me - what's been on your mind lately?",
            ProblemCategory.DEPRESSION_SADNESS: f"Hello, I'm {mitra_name}. I want you to know that reaching out today shows real strength. Depression can make everything feel heavy, but you don't have to carry it alone. I'm here to listen without judgment. How have you been feeling lately?",
            ProblemCategory.RELATIONSHIP_ISSUES: f"Hello, I'm {mitra_name}. Relationships can be one of the most rewarding and challenging parts of life. I'm here to listen and help you navigate whatever you're experiencing. What's been happening in your relationships that you'd like to talk about?",
            ProblemCategory.SELF_ESTEEM: f"Hi there, I'm {mitra_name}. Working on self-esteem takes courage, and I'm proud of you for taking this step. You deserve to feel good about yourself. I'm here to help you recognize your worth and build confidence. What's been affecting how you see yourself lately?",
            ProblemCategory.GRIEF_LOSS: f"Hello, I'm {mitra_name}. I'm so sorry for whatever loss you're experiencing. Grief is one of the most difficult journeys we face as humans. There's no right or wrong way to grieve, and I'm here to simply listen and support you through this. How are you doing today?",
            ProblemCategory.SOCIAL_ANXIETY: f"Hi, I'm {mitra_name}. I understand social situations can feel overwhelming. You're not alone in this. I'm here to help you build confidence and find strategies to feel more comfortable in social settings. What kind of situations have been challenging for you?",
            ProblemCategory.GENERAL_WELLNESS: f"Hello! I'm {mitra_name}, your AI wellness companion. I'm here to listen and support you through whatever you're going through today. There's no pressure to talk about anything specific - just know that this is your space to be heard. What's on your mind?"
        }

        return greetings.get(problem_category, greetings[ProblemCategory.GENERAL_WELLNESS])

    def get_session_info(self, session_id: str) -> Optional[VoiceSession]:
        """Get voice session information."""
        session_data = self.active_sessions.get(session_id)
        return session_data["session"] if session_data else None

    def get_active_sessions_count(self) -> int:
        """Get count of active voice sessions."""
        return len(self.active_sessions)

    async def _send_audio_to_client(self, session_id: str, audio_data: bytes):
        """Encodes audio data to base64 and sends it to the client via WebSocket."""
        await self._update_session_state(session_id, VoiceSessionState.TALKING)
        await self._send_to_client(session_id, {
            "type": "audio_chunk",
            "data": {
                "chunk": base64.b64encode(audio_data).decode('utf-8'),
                "timestamp": datetime.utcnow().isoformat(),
                "mime_type": "audio/pcm;rate=24000"
            }
        })

    async def _handle_transcript(self, session_id: str, role: str, text: str, is_final: bool = True):
        """Handles transcript updates and sends them to the client."""
        session_data = self.active_sessions.get(session_id)
        if not session_data: return

        if is_final:
            timestamp = datetime.utcnow()
            transcript_entry = {"role": role, "text": text, "timestamp": timestamp.isoformat()}
            session_data["transcript"].append(transcript_entry)
            session_data["session"].transcript.append(transcript_entry)

        await self._send_to_client(session_id, {
            "type": "transcript",
            "data": {
                "role": role,
                "text": text,
                "timestamp": datetime.utcnow().isoformat(),
                "is_final": is_final
            }
        })

        if role == "user" and is_final:
            await self._update_session_state(session_id, VoiceSessionState.PROCESSING)
        elif role == "assistant" and is_final:
            await self._update_session_state(session_id, VoiceSessionState.LISTENING)

    async def _update_session_state(self, session_id: str, new_state: VoiceSessionState):
        """Updates the session state and notifies the client."""
        session_data = self.active_sessions.get(session_id)
        if not session_data: return

        session_data["session"].state = new_state
        await self._send_to_client(session_id, {
            "type": "state_change",
            "data": {
                "state": new_state.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        })

    async def _send_usage_info(self, session_id: str, usage_metadata):
        """Sends token usage information to the client."""
        await self._send_to_client(session_id, {
            "type": "usage",
            "data": {"total_tokens": usage_metadata.total_token_count}
        })

    async def _send_error_to_client(self, session_id: str, message: str):
        """Sends an error message to the client."""
        await self._send_to_client(session_id, {
            "type": "error",
            "data": {"message": message}
        })

    async def _send_to_client(self, session_id: str, data: Dict[str, Any]):
        """Sends a JSON message to the client's WebSocket."""
        session_data = self.active_sessions.get(session_id)
        if session_data and session_data.get("websocket"):
            try:
                await session_data["websocket"].send_json(data)
            except (WebSocketDisconnect, RuntimeError) as e:
                logger.warning(f"Could not send to client for session {session_id}: {e}")


    async def end_voice_session(self, session_id: str):
        """Ends a voice session, updates its state, and triggers cleanup."""
        session_data = self.active_sessions.get(session_id)
        if not session_data: return

        voice_session = session_data["session"]
        if voice_session.state != VoiceSessionState.ENDED:
            voice_session.state = VoiceSessionState.ENDED
            voice_session.ended_at = datetime.utcnow()
            if voice_session.connected_at:
                duration = (voice_session.ended_at - voice_session.connected_at).total_seconds()
                voice_session.total_duration_seconds = int(duration)

            # Persist session to Firestore here if needed
            logger.info(f"Voice session {session_id} ended. Duration: {voice_session.total_duration_seconds}s")

        await self._cleanup_session(session_id)

    async def _cleanup_session(self, session_id: str):
        """Cleans up all resources associated with a voice session."""
        if session_id in self.active_sessions:
            session_data = self.active_sessions.pop(session_id)
            websocket = session_data.get("websocket")
            if websocket:
                try:
                    await websocket.close()
                except (WebSocketDisconnect, RuntimeError):
                    pass # Ignore errors on close
            logger.info(f"Cleaned up and removed session {session_id}")

    async def get_session_transcript(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves the transcript for a given session."""
        session_data = self.active_sessions.get(session_id)
        return session_data["transcript"] if session_data else []
