"""
Chat router for text and voice conversations with Mitra AI.
"""

import logging
from typing import List, Optional
from datetime import datetime
import uuid
import base64

from fastapi import APIRouter, HTTPException, Depends, Header, File, UploadFile
from fastapi.responses import Response

from models.chat import (
    TextChatRequest, VoiceChatRequest, ChatResponse, 
    MultimodalChatRequest, SessionSummaryRequest, SessionSummaryResponse,
    ChatSession, ChatMessage, MessageRole, MessageType, MessageContent,
    SafetyStatus, CrisisResponse, ChatMode
)
from models.common import APIResponse, ErrorResponse, ErrorType
from services.gemini_service import GeminiService
from services.safety_service import SafetyService
from repository.firestore_repository import FirestoreRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
def get_gemini_service() -> GeminiService:
    return GeminiService()

def get_safety_service() -> SafetyService:
    return SafetyService()

def get_repository() -> FirestoreRepository:
    return FirestoreRepository()

async def get_current_user(authorization: str = Header(None)) -> str:
    """Extract user ID from authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    # Extract token and verify (mock implementation)
    token = authorization.split(" ")[1]
    # In production, verify Firebase ID token here
    return f"user_{hash(token) % 10000}"  # Mock user ID


@router.post("/text", response_model=ChatResponse)
async def send_text_message(
    request: TextChatRequest,
    current_user: str = Depends(get_current_user),
    gemini_service: GeminiService = Depends(get_gemini_service),
    safety_service: SafetyService = Depends(get_safety_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Send a text message to Mitra AI."""
    try:
        # Get or create chat session
        session_id = request.session_id or str(uuid.uuid4())
        session = await repository.get_chat_session(current_user, session_id)
        
        if not session:
            # Create new session
            session = ChatSession(
                session_id=session_id,
                user_id=current_user,
                mode=ChatMode.TEXT,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                messages=[],
                is_active=True,
                total_messages=0
            )
            await repository.create_chat_session(session)
        
        # Create user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            type=MessageType.TEXT,
            content=MessageContent(text=request.message),
            timestamp=datetime.utcnow(),
            safety_status=SafetyStatus.SAFE
        )
        
        # Safety assessment
        safety_status, confidence, severity = await safety_service.assess_safety(
            request.message, 
            session.messages
        )
        
        user_message.safety_status = safety_status
        
        # Add user message to session
        await repository.add_message_to_session(current_user, session_id, user_message)
        
        # Check if crisis intervention is needed
        if safety_status == SafetyStatus.CRISIS:
            crisis_response = await safety_service.generate_crisis_response(severity, request.message)
            
            # Log safety incident
            await safety_service.log_safety_incident(
                current_user, 
                request.message,
                {
                    "status": safety_status.value,
                    "confidence": confidence,
                    "severity": severity.value if severity else None
                }
            )
            
            # Return crisis response instead of AI response
            return ChatResponse(
                session_id=session_id,
                message_id=user_message.id,
                response_text=crisis_response.message,
                safety_status=SafetyStatus.CRISIS,
                timestamp=datetime.utcnow()
            )
        
        # Generate AI response
        all_messages = session.messages + [user_message]
        response_text, grounding_sources, thinking_text = await gemini_service.generate_text_response(
            all_messages,
            include_grounding=request.include_grounding
        )
        
        # Generate image if requested
        generated_image = None
        if request.generate_image and "image" in request.message.lower():
            try:
                # Extract image prompt from message
                image_prompt = request.message
                generated_image = await gemini_service.generate_image(image_prompt)
            except Exception as e:
                logger.warning(f"Failed to generate image: {e}")
        
        # Create assistant message
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            type=MessageType.TEXT,
            content=MessageContent(
                text=response_text,
                image_data=generated_image
            ),
            timestamp=datetime.utcnow(),
            safety_status=SafetyStatus.SAFE,
            metadata={
                "grounding_sources": [source.dict() for source in grounding_sources] if grounding_sources else [],
                "thinking": thinking_text
            }
        )
        
        # Add assistant message to session
        await repository.add_message_to_session(current_user, session_id, assistant_message)
        
        return ChatResponse(
            session_id=session_id,
            message_id=assistant_message.id,
            response_text=response_text,
            generated_image=generated_image,
            safety_status=SafetyStatus.SAFE,
            grounding_sources=[source.dict() for source in grounding_sources] if grounding_sources else None,
            timestamp=datetime.utcnow(),
            thinking_text=thinking_text
        )
        
    except Exception as e:
        logger.error(f"Error in text chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.post("/voice", response_model=ChatResponse)
async def send_voice_message(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = None,
    response_format: str = "audio",
    current_user: str = Depends(get_current_user),
    gemini_service: GeminiService = Depends(get_gemini_service),
    safety_service: SafetyService = Depends(get_safety_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Send a voice message to Mitra AI."""
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Process voice input to text
        transcribed_text = await gemini_service.process_voice_input(audio_data)
        
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Get or create session
        session_id = session_id or str(uuid.uuid4())
        session = await repository.get_chat_session(current_user, session_id)
        
        if not session:
            session = ChatSession(
                session_id=session_id,
                user_id=current_user,
                mode=ChatMode.VOICE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                messages=[],
                is_active=True,
                total_messages=0
            )
            await repository.create_chat_session(session)
        
        # Create user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            type=MessageType.AUDIO,
            content=MessageContent(
                text=transcribed_text,
                audio_data=audio_data
            ),
            timestamp=datetime.utcnow(),
            safety_status=SafetyStatus.SAFE
        )
        
        # Safety assessment
        safety_status, confidence, severity = await safety_service.assess_safety(
            transcribed_text,
            session.messages
        )
        
        user_message.safety_status = safety_status
        await repository.add_message_to_session(current_user, session_id, user_message)
        
        # Crisis check
        if safety_status == SafetyStatus.CRISIS:
            crisis_response = await safety_service.generate_crisis_response(severity, transcribed_text)
            
            return ChatResponse(
                session_id=session_id,
                message_id=user_message.id,
                response_text=crisis_response.message,
                safety_status=SafetyStatus.CRISIS,
                timestamp=datetime.utcnow()
            )
        
        # Generate response
        all_messages = session.messages + [user_message]
        
        if response_format == "audio":
            # Generate voice response
            response_audio, transcription = await gemini_service.generate_voice_response(
                all_messages,
                voice="Puck",  # Could be from user preferences
                language="en"
            )
            
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                type=MessageType.AUDIO,
                content=MessageContent(
                    text=transcription,
                    audio_data=response_audio
                ),
                timestamp=datetime.utcnow(),
                safety_status=SafetyStatus.SAFE
            )
            
            await repository.add_message_to_session(current_user, session_id, assistant_message)
            
            return ChatResponse(
                session_id=session_id,
                message_id=assistant_message.id,
                response_text=transcription,
                response_audio=response_audio,
                safety_status=SafetyStatus.SAFE,
                timestamp=datetime.utcnow()
            )
        else:
            # Generate text response
            response_text, grounding_sources, thinking_text = await gemini_service.generate_text_response(all_messages)
            
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                type=MessageType.TEXT,
                content=MessageContent(text=response_text),
                timestamp=datetime.utcnow(),
                safety_status=SafetyStatus.SAFE
            )
            
            await repository.add_message_to_session(current_user, session_id, assistant_message)
            
            return ChatResponse(
                session_id=session_id,
                message_id=assistant_message.id,
                response_text=response_text,
                safety_status=SafetyStatus.SAFE,
                timestamp=datetime.utcnow()
            )
        
    except Exception as e:
        logger.error(f"Error in voice chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process voice message")


@router.post("/multimodal", response_model=ChatResponse)
async def send_multimodal_message(
    request: MultimodalChatRequest,
    current_user: str = Depends(get_current_user),
    gemini_service: GeminiService = Depends(get_gemini_service),
    safety_service: SafetyService = Depends(get_safety_service),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Send a multimodal message (text + image) to Mitra AI."""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        session = await repository.get_chat_session(current_user, session_id)
        
        if not session:
            session = ChatSession(
                session_id=session_id,
                user_id=current_user,
                mode=ChatMode.MULTIMODAL,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                messages=[],
                is_active=True,
                total_messages=0
            )
            await repository.create_chat_session(session)
        
        # Create user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            type=MessageType.IMAGE,
            content=MessageContent(
                text=request.text,
                image_data=request.image_data
            ),
            timestamp=datetime.utcnow(),
            safety_status=SafetyStatus.SAFE
        )
        
        # Safety assessment on text content
        if request.text:
            safety_status, confidence, severity = await safety_service.assess_safety(
                request.text,
                session.messages
            )
            user_message.safety_status = safety_status
        
        await repository.add_message_to_session(current_user, session_id, user_message)
        
        # Generate response based on operation
        all_messages = session.messages + [user_message]
        
        if request.operation == "generate":
            # Generate new image
            generated_image = await gemini_service.generate_image(request.text or "peaceful scene")
            response_text = "I've created an image for you based on your request."
            
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                type=MessageType.IMAGE,
                content=MessageContent(
                    text=response_text,
                    image_data=generated_image
                ),
                timestamp=datetime.utcnow(),
                safety_status=SafetyStatus.SAFE
            )
            
        elif request.operation == "edit" and request.image_data:
            # Edit existing image
            edited_image = await gemini_service.edit_image(request.image_data, request.text)
            response_text = "I've edited the image according to your instructions."
            
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                type=MessageType.IMAGE,
                content=MessageContent(
                    text=response_text,
                    image_data=edited_image
                ),
                timestamp=datetime.utcnow(),
                safety_status=SafetyStatus.SAFE
            )
            
        else:
            # Describe image
            response_text, _, thinking_text = await gemini_service.generate_text_response(all_messages)
            
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                type=MessageType.TEXT,
                content=MessageContent(text=response_text),
                timestamp=datetime.utcnow(),
                safety_status=SafetyStatus.SAFE,
                metadata={"thinking": thinking_text}
            )
        
        await repository.add_message_to_session(current_user, session_id, assistant_message)
        
        return ChatResponse(
            session_id=session_id,
            message_id=assistant_message.id,
            response_text=assistant_message.content.text,
            generated_image=assistant_message.content.image_data,
            safety_status=SafetyStatus.SAFE,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in multimodal chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process multimodal message")


@router.get("/session/{session_id}", response_model=SessionSummaryResponse)
async def get_session_summary(
    session_id: str,
    include_messages: bool = False,
    limit: int = 50,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get summary of a chat session."""
    try:
        session = await repository.get_chat_session(current_user, session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        recent_messages = None
        if include_messages:
            recent_messages = session.messages[-limit:] if session.messages else []
        
        return SessionSummaryResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            mode=session.mode,
            created_at=session.created_at,
            updated_at=session.updated_at,
            total_messages=session.total_messages,
            context_summary=session.context_summary,
            recent_messages=recent_messages,
            is_active=session.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session summary")


@router.get("/sessions", response_model=List[SessionSummaryResponse])
async def get_user_sessions(
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get list of user's chat sessions."""
    try:
        # In production, this would query user's sessions from Firestore
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Delete a chat session."""
    try:
        # In production, implement session deletion
        logger.info(f"Mock: Deleting session {session_id} for user {current_user}")
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")