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

from google import genai
from google.genai import types

from .base_gemini_service import BaseGeminiService
from core.config import settings
from models.user import UserProfile, ProblemCategory, VoiceOption
from models.wellness import VoiceSession, VoiceSessionState, VoiceTranscriptEvent, VoiceInterruptionEvent

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

        Args:
            user_id: User ID
            user_profile: User profile for personalization
            problem_category: Problem category for context
            voice_option: Voice preference (Puck, Charon, Kore, etc.)
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
                "transcript": [],
                "audio_buffer": b"",
                "is_speaking": False,
                "conversation_started": False
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
        Start the Live API conversation with continuous audio streaming.

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

            # Configure Live API for phone call-like experience
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice_session.voice_option
                        }
                    }
                },
                # Enable both input and output transcription
                "input_audio_transcription": {},
                "output_audio_transcription": {},
                # Configure VAD for natural conversation flow
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

            # Add personalized system instruction for mental health support
            system_instruction = self._get_personalized_system_instruction(
                user_profile, voice_session.problem_category
            )

            # Create the Live API connection context manager
            live_connection = self.client.aio.live.connect(
                model="gemini-live-2.5-flash-preview",  # Use the correct Live API model
                config=config
            )
            
            # Enter the context manager and store the session
            live_session = await live_connection.__aenter__()
            
            # Store live session, context manager, and websocket
            session_data["live_session"] = live_session
            session_data["live_connection"] = live_connection
            session_data["websocket"] = websocket

            # Update session state
            voice_session.state = VoiceSessionState.CONNECTED
            voice_session.connected_at = datetime.utcnow()

            # Start handling Live API messages in background
            asyncio.create_task(self._handle_live_session(session_id))

            # Send initial greeting to start the conversation
            await self._send_initial_greeting(session_id, system_instruction)

            logger.info(f"Started Live API conversation for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error starting live conversation: {e}")
            await self._update_session_state(session_id, VoiceSessionState.ERROR)
            return False

    async def _handle_live_session(self, session_id: str):
        """
        Handle Live API session messages for continuous conversation.

        Args:
            session_id: Voice session ID
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            live_session = session_data["live_session"]
            websocket = session_data["websocket"]

            async for message in live_session.receive():
                await self._process_live_message(session_id, message)

        except Exception as e:
            logger.error(f"Error handling live session {session_id}: {e}")
            await self._update_session_state(session_id, VoiceSessionState.ERROR)
        finally:
            # Clean up session
            await self._cleanup_session(session_id)

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

            # Log the message type for debugging
            logger.debug(f"Live API message type: {type(message)}, has audio: {hasattr(message, 'audio')}")

            # Handle different message types based on the Live API response format
            # The message could be a string, audio data, or a structured response
            
            # Handle audio output
            if hasattr(message, 'audio') and message.audio is not None:
                # This is audio output from the model
                await websocket.send_json({
                    "type": "audio_chunk",
                    "data": base64.b64encode(message.audio).decode(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "mime_type": "audio/pcm;rate=24000"  # Live API outputs at 24kHz
                })
                await self._update_session_state(session_id, VoiceSessionState.TALKING)
            
            # Handle text transcript
            elif hasattr(message, 'text') and message.text is not None:
                await self._handle_transcript(session_id, "assistant", message.text, is_final=True)
            
            # Handle raw bytes (audio data)
            elif isinstance(message, bytes):
                await websocket.send_json({
                    "type": "audio_chunk",
                    "data": base64.b64encode(message).decode(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "mime_type": "audio/pcm;rate=24000"
                })
                await self._update_session_state(session_id, VoiceSessionState.TALKING)
            
            # Handle string messages (could be transcripts)
            elif isinstance(message, str):
                await self._handle_transcript(session_id, "assistant", message, is_final=True)

        except Exception as e:
            logger.error(f"Error processing live message for session {session_id}: {e}")


    async def send_audio_input(self, session_id: str, audio_data: bytes, mime_type: str = "audio/pcm;rate=16000"):
        """
        Send audio input to Live API for continuous conversation.

        Args:
            session_id: Voice session ID
            audio_data: Raw audio bytes
            mime_type: Audio MIME type
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data or not session_data["live_session"]:
                logger.error(f"No active live session for {session_id}")
                return

            live_session = session_data["live_session"]

            # Send audio data to Live API
            await live_session.send_audio(audio_data)

            # Update session state
            if not session_data["is_speaking"]:
                session_data["is_speaking"] = True
                await self._update_session_state(session_id, VoiceSessionState.PROCESSING)

        except Exception as e:
            logger.error(f"Error sending audio input: {e}")

    async def send_audio_stream_end(self, session_id: str):
        """
        Signal end of audio stream to Live API.

        Args:
            session_id: Voice session ID
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data or not session_data["live_session"]:
                return

            live_session = session_data["live_session"]

            # Audio stream end is handled automatically by the Live API with VAD
            # Just update the speaking state
            pass

            # Update speaking state
            session_data["is_speaking"] = False

        except Exception as e:
            logger.error(f"Error ending audio stream: {e}")

    async def _send_initial_greeting(self, session_id: str, system_instruction: str):
        """Send initial greeting to start the conversation."""
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            voice_session = session_data["session"]
            user_profile = session_data["user_profile"]
            live_session = session_data["live_session"]

            # Create personalized greeting
            user_name = user_profile.display_name if user_profile else "there"
            mitra_name = user_profile.preferences.mitra_name if user_profile and user_profile.preferences else "Mitra"

            greeting = f"Hello {user_name}! I'm {mitra_name}, your AI wellness companion. I'm here to listen and support you through whatever you're going through. How are you feeling today?"

            if voice_session.problem_category:
                category_greeting = self._get_category_specific_greeting(voice_session.problem_category, mitra_name)
                greeting = category_greeting

            # Send the system instruction and greeting as initial message
            initial_message = f"{system_instruction}\n\nPlease start the conversation with this greeting: {greeting}"
            
            # Send initial message to start the conversation
            await live_session.send_text(initial_message)

            session_data["conversation_started"] = True

        except Exception as e:
            logger.error(f"Error sending initial greeting: {e}")

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

    async def _handle_transcript(self, session_id: str, role: str, text: str, is_final: bool = True):
        """
        Handle transcript updates.

        Args:
            session_id: Voice session ID
            role: Speaker role (user/assistant)
            text: Transcript text
            is_final: Whether this is a final transcript
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            websocket = session_data["websocket"]
            timestamp = datetime.utcnow()

            # Add to session transcript if final
            if is_final:
                transcript_entry = {
                    "role": role,
                    "text": text,
                    "timestamp": timestamp.isoformat()
                }
                session_data["transcript"].append(transcript_entry)
                session_data["session"].transcript.append(transcript_entry)

            # Send transcript to client
            await websocket.send_json({
                "type": "transcript",
                "data": {
                    "role": role,
                    "text": text,
                    "timestamp": timestamp.isoformat(),
                    "is_final": is_final
                }
            })

            # Update session state based on role
            if role == "user" and is_final:
                await self._update_session_state(session_id, VoiceSessionState.PROCESSING)
            elif role == "assistant" and is_final:
                await self._update_session_state(session_id, VoiceSessionState.LISTENING)

            logger.debug(f"Transcript - {role}: {text[:50]}...")

        except Exception as e:
            logger.error(f"Error handling transcript: {e}")

    async def _handle_interruption(self, session_id: str):
        """
        Handle voice interruption when user starts speaking.

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

            # Update session state
            await self._update_session_state(session_id, VoiceSessionState.LISTENING)

            logger.info(f"Voice interruption handled for session {session_id}")

        except Exception as e:
            logger.error(f"Error handling interruption: {e}")

    async def _update_session_state(self, session_id: str, new_state: VoiceSessionState):
        """
        Update voice session state.

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

            # Update session state
            voice_session.state = new_state

            # Send state update to client
            await websocket.send_json({
                "type": "state_change",
                "data": {
                    "session_id": session_id,
                    "state": new_state.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })

        except Exception as e:
            logger.error(f"Error updating session state: {e}")

    async def _send_usage_info(self, session_id: str, usage_metadata):
        """Send token usage information to client."""
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            websocket = session_data["websocket"]

            usage_data = {
                "total_tokens": usage_metadata.total_token_count
            }

            # Add detailed token breakdown if available
            if hasattr(usage_metadata, 'response_tokens_details'):
                details = {}
                for detail in usage_metadata.response_tokens_details:
                    if hasattr(detail, 'modality') and hasattr(detail, 'token_count'):
                        details[detail.modality] = detail.token_count
                usage_data["details"] = details

            await websocket.send_json({
                "type": "usage",
                "data": usage_data
            })

        except Exception as e:
            logger.error(f"Error sending usage info: {e}")

    async def end_voice_session(self, session_id: str):
        """
        End a voice session and clean up resources.

        Args:
            session_id: Voice session ID
        """
        try:
            session_data = self.active_sessions.get(session_id)
            if not session_data:
                return

            voice_session = session_data["session"]

            # Update session end time
            voice_session.state = VoiceSessionState.ENDED
            voice_session.ended_at = datetime.utcnow()

            if voice_session.connected_at:
                duration = (voice_session.ended_at - voice_session.connected_at).total_seconds()
                voice_session.total_duration_seconds = int(duration)

            # Close live session if active
            if session_data.get("live_connection"):
                try:
                    await session_data["live_connection"].__aexit__(None, None, None)
                except:
                    pass

            # Save session data to repository if needed
            # TODO: Implement session persistence

            logger.info(f"Voice session {session_id} ended. Duration: {voice_session.total_duration_seconds}s")

        except Exception as e:
            logger.error(f"Error ending voice session: {e}")
        finally:
            # Remove from active sessions
            await self._cleanup_session(session_id)

    async def _cleanup_session(self, session_id: str):
        """Clean up session resources."""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]

                # Close WebSocket if still connected
                websocket = session_data.get("websocket")
                if websocket:
                    try:
                        await websocket.close()
                    except:
                        pass

                # Remove from active sessions
                del self.active_sessions[session_id]

            logger.info(f"Cleaned up session {session_id}")

        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")

    async def get_session_transcript(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get session transcript.

        Args:
            session_id: Voice session ID

        Returns:
            List of transcript entries
        """
        session_data = self.active_sessions.get(session_id)
        if session_data:
            return session_data["transcript"]
        return []
