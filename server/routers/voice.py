"""
Voice conversation router with WebSocket support for real-time Live API interactions.
"""

import logging
import json
import asyncio
import uuid
import base64
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Header
from fastapi.responses import JSONResponse

from models.wellness import VoiceSessionRequest, VoiceSessionResponse, VoiceSessionState
from models.user import UserProfile, ProblemCategory
from services.live_voice_service import LiveVoiceService
from repository.firestore_repository import FirestoreRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
def get_live_voice_service() -> LiveVoiceService:
    return LiveVoiceService()

def get_repository() -> FirestoreRepository:
    return FirestoreRepository()

async def get_current_user(authorization: str = Header(None)) -> str:
    """Extract user ID from Firebase ID token in authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    try:
        # Extract token and verify with Firebase
        token = authorization.split(" ")[1]

        # Initialize Firebase service to verify token
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()

        # Verify ID token and extract claims
        decoded_token = await firebase_service.verify_id_token(token)

        # Return the user ID from the verified token
        return decoded_token.get('uid')

    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired authorization token")


@router.post("/voice/start", response_model=VoiceSessionResponse)
async def start_voice_session(
    request: VoiceSessionRequest,
    current_user: str = Depends(get_current_user),
    voice_service: LiveVoiceService = Depends(get_live_voice_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Start a new voice conversation session."""
    try:
        logger.info(f"Starting voice session for user {current_user}")

        # Get user profile for personalization
        user_profile = await repository.get_user(current_user)

        # Create voice session
        voice_session = await voice_service.create_voice_session(
            user_id=current_user,
            user_profile=user_profile,
            problem_category=request.problem_category,
            voice_option=request.voice_option,
            language=request.language
        )

        # Generate WebSocket URL
        websocket_url = f"/api/v1/voice/connect/{voice_session.session_id}"

        return VoiceSessionResponse(
            session_id=voice_session.session_id,
            state=voice_session.state,
            websocket_url=websocket_url,
            created_at=voice_session.created_at
        )

    except Exception as e:
        logger.error(f"Error starting voice session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start voice session")


@router.websocket("/voice/connect/{session_id}")
async def voice_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """WebSocket endpoint for real-time voice conversation."""
    await websocket.accept()
    logger.info(f"WebSocket connected for voice session {session_id}")

    try:
        # Start Live API conversation
        success = await voice_service.start_live_conversation(session_id, websocket)

        if not success:
            await websocket.send_json({
                "type": "error",
                "data": {"message": "Failed to start voice conversation"}
            })
            await websocket.close()
            return

        # Send connection success
        await websocket.send_json({
            "type": "connected",
            "data": {
                "session_id": session_id,
                "message": "Voice conversation started",
                "timestamp": voice_service.get_session_info(session_id).connected_at.isoformat()
            }
        })

        # Handle WebSocket messages
        while True:
            try:
                # Receive message from client
                message = await websocket.receive_json()
                await _handle_websocket_message(websocket, session_id, message, voice_service)

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON message"}
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Error processing message"}
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        # Clean up voice session
        await voice_service.end_voice_session(session_id)


async def _handle_websocket_message(
    websocket: WebSocket,
    session_id: str,
    message: dict,
    voice_service: LiveVoiceService
):
    """
    Handle incoming WebSocket messages.

    Args:
        websocket: WebSocket connection
        session_id: Voice session ID
        message: WebSocket message
        voice_service: Voice service instance
    """
    try:
        message_type = message.get("type")
        data = message.get("data", {})

        if message_type == "audio":
            # Handle audio input from client
            audio_data_b64 = data.get("audio")
            if audio_data_b64:
                # Decode base64 audio data
                audio_data = base64.b64decode(audio_data_b64)

                # Send to Live API
                await voice_service.send_audio_input(session_id, audio_data)
            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "No audio data provided"}
                })

        elif message_type == "audio_end":
            # Handle end of audio stream
            session_data = voice_service.active_sessions.get(session_id)
            if session_data and session_data["live_session"]:
                # Send audio stream end to Live API
                await session_data["live_session"].send_realtime_input(audio_stream_end=True)

        elif message_type == "ping":
            # Handle ping/pong for connection health
            await websocket.send_json({
                "type": "pong",
                "data": {"timestamp": data.get("timestamp")}
            })

        elif message_type == "end_session":
            # Handle session termination request
            await voice_service.end_voice_session(session_id)
            await websocket.send_json({
                "type": "session_ended",
                "data": {"session_id": session_id}
            })
            await websocket.close()

        else:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Unknown message type: {message_type}"}
            })

    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": "Error processing message"}
        })


@router.get("/voice/session/{session_id}")
async def get_voice_session(
    session_id: str,
    current_user: str = Depends(get_current_user),
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """Get voice session information."""
    try:
        voice_session = voice_service.get_session_info(session_id)

        if not voice_session:
            raise HTTPException(status_code=404, detail="Voice session not found")

        if voice_session.user_id != current_user:
            raise HTTPException(status_code=403, detail="Access denied")

        return {
            "session_id": voice_session.session_id,
            "state": voice_session.state.value,
            "problem_category": voice_session.problem_category.value if voice_session.problem_category else None,
            "voice_option": voice_session.voice_option,
            "language": voice_session.language,
            "created_at": voice_session.created_at.isoformat(),
            "connected_at": voice_session.connected_at.isoformat() if voice_session.connected_at else None,
            "total_duration_seconds": voice_session.total_duration_seconds,
            "transcript_length": len(voice_session.transcript)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice session")


@router.delete("/voice/session/{session_id}")
async def end_voice_session(
    session_id: str,
    current_user: str = Depends(get_current_user),
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """End a voice session."""
    try:
        voice_session = voice_service.get_session_info(session_id)

        if not voice_session:
            raise HTTPException(status_code=404, detail="Voice session not found")

        if voice_session.user_id != current_user:
            raise HTTPException(status_code=403, detail="Access denied")

        await voice_service.end_voice_session(session_id)

        return {
            "message": "Voice session ended successfully",
            "session_id": session_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending voice session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end voice session")


@router.get("/voice/sessions")
async def get_active_sessions_info(
    current_user: str = Depends(get_current_user),
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """Get information about active voice sessions."""
    try:
        # Get user's active sessions
        user_sessions = []
        for session_data in voice_service.active_sessions.values():
            voice_session = session_data["session"]
            if voice_session.user_id == current_user:
                user_sessions.append({
                    "session_id": voice_session.session_id,
                    "state": voice_session.state.value,
                    "problem_category": voice_session.problem_category.value if voice_session.problem_category else None,
                    "created_at": voice_session.created_at.isoformat(),
                    "connected_at": voice_session.connected_at.isoformat() if voice_session.connected_at else None
                })

        return {
            "active_sessions": user_sessions,
            "total_active": len(user_sessions)
        }

    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active sessions")


@router.get("/voice/health")
async def voice_service_health(
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """Get voice service health information."""
    try:
        return {
            "service": "voice_conversation",
            "status": "healthy",
            "active_sessions": voice_service.get_active_sessions_count(),
            "gemini_live_model": voice_service.client is not None,
            "timestamp": voice_service.get_active_sessions_count()
        }

    except Exception as e:
        logger.error(f"Error checking voice service health: {e}")
        return {
            "service": "voice_conversation",
            "status": "unhealthy",
            "error": str(e)
        }
