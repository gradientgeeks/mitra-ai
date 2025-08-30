"""
Pydantic models for chat-related data structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Import problem categories from user models
from models.user import ProblemCategory
# Import resource types from wellness models
from models.wellness import ResourceType, GeneratedResource


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Types of messages."""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    STRUCTURED = "structured"


class ChatMode(str, Enum):
    """Chat interaction modes."""
    TEXT = "text"
    VOICE = "voice"
    MULTIMODAL = "multimodal"


class SafetyStatus(str, Enum):
    """Safety assessment status."""
    SAFE = "safe"
    WARNING = "warning"
    CRISIS = "crisis"


class MessageContent(BaseModel):
    """Content of a message."""
    text: Optional[str] = None
    audio_data: Optional[bytes] = None
    image_data: Optional[bytes] = None
    structured_data: Optional[Dict[str, Any]] = None
    html_content: Optional[str] = None


class ChatMessage(BaseModel):
    """Individual chat message."""
    id: str = Field(..., description="Unique message ID")
    role: MessageRole
    type: MessageType
    content: MessageContent
    timestamp: datetime
    safety_status: SafetyStatus = SafetyStatus.SAFE
    metadata: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    """Chat session data."""
    session_id: str = Field(..., description="Unique session ID")
    user_id: str = Field(..., description="User ID")
    mode: ChatMode = ChatMode.TEXT
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
    is_active: bool = True
    context_summary: Optional[str] = None
    total_messages: int = 0
    problem_category: Optional[ProblemCategory] = None
    generated_resources: List[Dict[str, Any]] = []


class TextChatRequest(BaseModel):
    """Request for text-based chat."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    include_grounding: bool = False
    generate_image: bool = False
    problem_category: Optional[ProblemCategory] = None


class VoiceChatRequest(BaseModel):
    """Request for voice-based chat."""
    audio_data: bytes = Field(..., description="PCM audio data")
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    session_id: Optional[str] = None
    response_format: str = Field(default="audio", pattern="^(audio|text)$")
    problem_category: Optional[ProblemCategory] = None


class ChatResponse(BaseModel):
    """Response from chat interaction."""
    session_id: str
    message_id: str
    response_text: Optional[str] = None
    response_audio: Optional[bytes] = None
    response_html: Optional[str] = None
    generated_image: Optional[bytes] = None
    safety_status: SafetyStatus
    grounding_sources: Optional[List[Dict[str, str]]] = None
    timestamp: datetime
    thinking_text: Optional[str] = None
    generated_resources: Optional[List[Dict[str, Any]]] = None


class MultimodalChatRequest(BaseModel):
    """Request for multimodal chat (text + image)."""
    text: Optional[str] = None
    image_data: Optional[bytes] = None
    session_id: Optional[str] = None
    operation: str = Field(default="describe", pattern="^(describe|edit|generate)$")
    problem_category: Optional[ProblemCategory] = None


class SessionSummaryRequest(BaseModel):
    """Request to get session summary."""
    session_id: str
    include_messages: bool = False
    limit: Optional[int] = Field(default=50, le=100)


class SessionSummaryResponse(BaseModel):
    """Response with session summary."""
    session_id: str
    user_id: str
    mode: ChatMode
    created_at: datetime
    updated_at: datetime
    total_messages: int
    context_summary: Optional[str] = None
    recent_messages: Optional[List[ChatMessage]] = None
    is_active: bool
    problem_category: Optional[ProblemCategory] = None
    generated_resources: List[Dict[str, Any]] = []


class CrisisResponse(BaseModel):
    """Response when crisis is detected."""
    crisis_detected: bool = True
    severity: str = Field(..., pattern="^(moderate|high|severe)$")
    message: str
    helplines: Dict[str, Dict[str, str]]
    immediate_actions: List[str]
    timestamp: datetime



class SessionResourcesRequest(BaseModel):
    """Request to generate resources for a session."""
    session_id: str
    resource_types: List[ResourceType] = []
    max_resources: int = Field(default=3, ge=1, le=10)


class SessionResourcesResponse(BaseModel):
    """Response with generated session resources."""
    session_id: str
    resources: List[GeneratedResource]
    problem_category: ProblemCategory
    generated_at: datetime