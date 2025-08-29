"""
Pydantic models for chat-related data structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ProblemCategory(str, Enum):
    """Mental health problem categories for session context."""
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    LONELINESS = "loneliness"
    ACADEMIC_PRESSURE = "academic_pressure"
    RELATIONSHIP_ISSUES = "relationship_issues"
    SELF_ESTEEM = "self_esteem"
    CAREER_CONFUSION = "career_confusion"
    FAMILY_PROBLEMS = "family_problems"
    GENERAL_WELLBEING = "general_wellbeing"


class ResourceType(str, Enum):
    """Types of resources that can be generated."""
    ARTICLE = "article"
    EXERCISE = "exercise"
    MEDITATION = "meditation"
    COPING_STRATEGY = "coping_strategy"
    BREATHING_TECHNIQUE = "breathing_technique"
    PROFESSIONAL_HELP = "professional_help"


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
    problem_categories: List[ProblemCategory] = []
    generated_resources: List[Dict[str, Any]] = []
    session_mood_start: Optional[int] = None
    session_mood_end: Optional[int] = None


class TextChatRequest(BaseModel):
    """Request for text-based chat."""
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    include_grounding: bool = Field(default=False, description="Include web search grounding")
    generate_image: bool = Field(default=False, description="Generate image based on message content")
    problem_categories: List[ProblemCategory] = Field(default=[], description="Current conversation problem categories")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="User context including age_group, gender, mitra_name, etc.")


class VoiceChatRequest(BaseModel):
    """Request for voice-based chat."""
    audio_data: bytes = Field(..., description="Audio data")
    session_id: Optional[str] = None
    voice_preference: Optional[str] = Field(default="Puck", description="Preferred voice for response")
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    problem_categories: List[ProblemCategory] = Field(default=[], description="Current conversation problem categories")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="User context including age_group, gender, etc.")


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
    suggested_problem_categories: List[ProblemCategory] = []
    generated_resources: List[Dict[str, Any]] = []


class MultimodalChatRequest(BaseModel):
    """Request for multimodal chat (text + image)."""
    text: str = Field(..., min_length=1, max_length=4000)
    image_data: Optional[bytes] = None
    session_id: Optional[str] = None
    operation: str = Field(default="describe", description="Operation: generate, edit, or describe")
    problem_categories: List[ProblemCategory] = Field(default=[], description="Current conversation problem categories")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="User context including age_group, gender, etc.")


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
    problem_categories: List[ProblemCategory] = []
    generated_resources: List[Dict[str, Any]] = []
    session_mood_start: Optional[int] = None
    session_mood_end: Optional[int] = None


class SessionEndRequest(BaseModel):
    """Request to end a session and generate resources."""
    session_id: str
    final_mood: Optional[int] = Field(None, ge=1, le=10, description="User's mood at session end")
    generate_resources: bool = Field(default=True, description="Whether to generate helpful resources")


class SessionResourcesResponse(BaseModel):
    """Response with generated session resources."""
    session_id: str
    problem_categories: List[ProblemCategory]
    resources: List[Dict[str, Any]]
    summary: str
    follow_up_suggestions: List[str]
    mood_improvement_tips: List[str] = []


class UpdateSessionCategoriesRequest(BaseModel):
    """Request to update session problem categories."""
    session_id: str
    problem_categories: List[ProblemCategory]
    add_categories: bool = Field(default=True, description="Whether to add to existing or replace")


class CrisisResponse(BaseModel):
    """Response when crisis is detected."""
    crisis_detected: bool = True
    severity: str = Field(..., pattern="^(moderate|high|severe)$")
    message: str
    helplines: Dict[str, Dict[str, str]]
    immediate_actions: List[str]
    timestamp: datetime