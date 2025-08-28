"""
Models package for Mitra AI server.
"""

from .user import (
    UserProvider,
    UserStatus,
    UserPreferences,
    UserProfile,
    CreateUserRequest,
    UpdateUserRequest,
    LinkAccountRequest,
    UserResponse
)

from .chat import (
    MessageRole,
    MessageType,
    ChatMode,
    SafetyStatus,
    MessageContent,
    ChatMessage,
    ChatSession,
    TextChatRequest,
    VoiceChatRequest,
    ChatResponse,
    MultimodalChatRequest,
    SessionSummaryRequest,
    SessionSummaryResponse,
    CrisisResponse
)

from .wellness import (
    MoodLevel,
    EmotionTag,
    MeditationType,
    JournalType,
    MoodEntry,
    CreateMoodEntryRequest,
    UpdateMoodEntryRequest,
    MoodAnalysis,
    JournalEntry,
    CreateJournalEntryRequest,
    UpdateJournalEntryRequest,
    MeditationSession,
    GenerateMeditationRequest,
    MeditationResponse,
    WellnessInsight,
    WellnessDashboard
)

from .common import (
    APIStatus,
    ErrorType,
    APIResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
    HealthCheck,
    GroundingSource,
    GenerationConfig
)

__all__ = [
    # User models
    "UserProvider", "UserStatus", "UserPreferences", "UserProfile",
    "CreateUserRequest", "UpdateUserRequest", "LinkAccountRequest", "UserResponse",
    
    # Chat models
    "MessageRole", "MessageType", "ChatMode", "SafetyStatus",
    "MessageContent", "ChatMessage", "ChatSession",
    "TextChatRequest", "VoiceChatRequest", "ChatResponse",
    "MultimodalChatRequest", "SessionSummaryRequest", "SessionSummaryResponse",
    "CrisisResponse",
    
    # Wellness models
    "MoodLevel", "EmotionTag", "MeditationType", "JournalType",
    "MoodEntry", "CreateMoodEntryRequest", "UpdateMoodEntryRequest", "MoodAnalysis",
    "JournalEntry", "CreateJournalEntryRequest", "UpdateJournalEntryRequest",
    "MeditationSession", "GenerateMeditationRequest", "MeditationResponse",
    "WellnessInsight", "WellnessDashboard",
    
    # Common models
    "APIStatus", "ErrorType", "APIResponse", "ErrorResponse",
    "PaginationParams", "PaginatedResponse", "HealthCheck",
    "GroundingSource", "GenerationConfig"
]