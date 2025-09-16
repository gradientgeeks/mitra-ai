"""
Voice conversation router with WebSocket support for real-time Live API interactions.
"""

import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Header

from models.wellness import VoiceSessionRequest, VoiceSessionResponse
from models.user import UserProfile
from services.live_voice_service import LiveVoiceService
from repository.firestore_repository import FirestoreRepository
from services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection using a singleton pattern for the service
@router.on_event("startup")
async def startup_event():
    global _live_voice_service_instance
    _live_voice_service_instance = LiveVoiceService()
    global _firebase_service_instance
    _firebase_service_instance = FirebaseService()

def get_live_voice_service() -> LiveVoiceService:
    return _live_voice_service_instance

def get_firebase_service() -> FirebaseService:
    return _firebase_service_instance

def get_repository() -> FirestoreRepository:
    return FirestoreRepository()


async def get_current_user(authorization: str = Header(None)) -> str:
    """Extracts user ID from Firebase ID token in the authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    try:
        token = authorization.split(" ")[1]
        firebase_service = get_firebase_service()
        decoded_token = await firebase_service.verify_id_token(token)
        return decoded_token.get('uid')
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired authorization token")


async def get_current_user_from_token(token: str) -> str:
    """Extracts user ID from a Firebase ID token string."""
    try:
        firebase_service = get_firebase_service()
        decoded_token = await firebase_service.verify_id_token(token)
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
    """Starts a new voice conversation session."""
    try:
        logger.info(f"Starting voice session for user {current_user}")
        user_profile = await repository.get_user(current_user)
        voice_session = await voice_service.create_voice_session(
            user_id=current_user,
            user_profile=user_profile,
            problem_category=request.problem_category,
            voice_option=request.voice_option,
            language=request.language
        )
        websocket_url = f"/voice/connect/{voice_session.session_id}"
        return VoiceSessionResponse(
            session_id=voice_session.session_id,
            state=voice_session.state,
            websocket_url=websocket_url,
            created_at=voice_session.created_at
        )
    except Exception as e:
        logger.error(f"Error starting voice session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start voice session")


@router.websocket("/voice/connect/{session_id}")
async def voice_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """Handles the WebSocket connection for a real-time voice conversation."""
    await websocket.accept()
    
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008, reason="Authentication token required")
            return

        current_user = await get_current_user_from_token(token)
        logger.info(f"Authenticated WebSocket for user: {current_user}")

        voice_session = voice_service.get_session_info(session_id)
        if not voice_session or voice_session.user_id != current_user:
            logger.error(f"Session verification failed for session {session_id} and user {current_user}")
            await websocket.close(code=1008, reason="Session not found or access denied")
            return

    except HTTPException as e:
        await websocket.close(code=1008, reason=e.detail)
        return
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}", exc_info=True)
        await websocket.close(code=1008, reason="Authentication failed")
        return

    logger.info(f"Handing off WebSocket for session {session_id} to LiveVoiceService")
    await voice_service.handle_voice_call(session_id, websocket)


@router.get("/voice/session/{session_id}")
async def get_voice_session(
    session_id: str,
    current_user: str = Depends(get_current_user),
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """Gets voice session information."""
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


@router.delete("/voice/session/{session_id}")
async def end_voice_session_endpoint(
    session_id: str,
    current_user: str = Depends(get_current_user),
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """Ends a voice session."""
    voice_session = voice_service.get_session_info(session_id)
    if not voice_session:
        raise HTTPException(status_code=404, detail="Voice session not found")
    if voice_session.user_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    await voice_service.end_voice_session(session_id)
    return {"message": "Voice session ended successfully", "session_id": session_id}


@router.get("/voice/sessions")
async def get_active_sessions_info(
    current_user: str = Depends(get_current_user),
    voice_service: LiveVoiceService = Depends(get_live_voice_service)
):
    """Gets information about the current user's active voice sessions."""
    user_sessions = []
    for session_data in voice_service.active_sessions.values():
        voice_session = session_data["session"]
        if voice_session.user_id == current_user:
            user_sessions.append({
                "session_id": voice_session.session_id,
                "state": voice_session.state.value,
                "created_at": voice_session.created_at.isoformat(),
            })
    return {"active_sessions": user_sessions}


@router.get("/voice/health")
async def voice_service_health(voice_service: LiveVoiceService = Depends(get_live_voice_service)):
    """Gets voice service health information."""
    return {
        "service": "voice_conversation",
        "status": "healthy",
        "active_sessions": voice_service.get_active_sessions_count(),
        "gemini_live_model": voice_service.client is not None,
        "timestamp": datetime.utcnow().isoformat()
    }
