"""
Pydantic models for wellness-related data structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

# Import problem categories from user models
from models.user import ProblemCategory


class MoodLevel(int, Enum):
    """Mood levels from 1-10."""
    VERY_LOW = 1
    LOW = 2
    QUITE_LOW = 3
    SLIGHTLY_LOW = 4
    NEUTRAL = 5
    SLIGHTLY_HIGH = 6
    QUITE_HIGH = 7
    HIGH = 8
    VERY_HIGH = 9
    EXCELLENT = 10


class EmotionTag(str, Enum):
    """Common emotion tags."""
    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    CALM = "calm"
    EXCITED = "excited"
    ANGRY = "angry"
    CONFUSED = "confused"
    GRATEFUL = "grateful"
    LONELY = "lonely"
    HOPEFUL = "hopeful"
    OVERWHELMED = "overwhelmed"


class MeditationType(str, Enum):
    """Types of meditation."""
    BREATHING = "breathing"
    MINDFULNESS = "mindfulness"
    BODY_SCAN = "body_scan"
    LOVING_KINDNESS = "loving_kindness"
    SLEEP = "sleep"
    STRESS_RELIEF = "stress_relief"


class JournalType(str, Enum):
    """Types of journal entries."""
    DAILY_REFLECTION = "daily_reflection"
    GRATITUDE = "gratitude"
    GOALS = "goals"
    CHALLENGES = "challenges"
    ACHIEVEMENTS = "achievements"
    FREE_FORM = "free_form"


class ResourceType(str, Enum):
    """Types of wellness resources."""
    MEDITATION = "meditation"
    BREATHING_EXERCISE = "breathing_exercise"
    COPING_STRATEGIES = "coping_strategies"
    AFFIRMATIONS = "affirmations"
    ARTICLES = "articles"
    VIDEOS = "videos"
    WORKSHEETS = "worksheets"
    EMERGENCY_CONTACTS = "emergency_contacts"


class GeneratedResource(BaseModel):
    """Generated wellness resource."""
    id: str = Field(..., description="Unique resource ID")
    type: ResourceType
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=500)
    content: str = Field(..., description="Main resource content")
    duration_minutes: Optional[int] = Field(None, ge=1, le=120)
    difficulty_level: str = Field("beginner", pattern="^(beginner|intermediate|advanced)$")
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    problem_category: ProblemCategory
    metadata: Optional[Dict[str, Any]] = None


class MoodEntry(BaseModel):
    """Daily mood entry."""
    id: str = Field(..., description="Unique entry ID")
    user_id: str = Field(..., description="User ID")
    date: date
    mood_level: MoodLevel
    emotion_tags: List[EmotionTag] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=500)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class JournalEntry(BaseModel):
    """Journal entry for reflection."""
    id: str = Field(..., description="Unique entry ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field(None, max_length=100)
    content: str = Field(..., min_length=1, max_length=5000)
    mood_before: Optional[MoodLevel] = None
    mood_after: Optional[MoodLevel] = None
    tags: List[str] = Field(default_factory=list)
    is_private: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class MeditationSession(BaseModel):
    """Meditation session record."""
    id: str = Field(..., description="Unique session ID")
    user_id: str = Field(..., description="User ID")
    type: MeditationType
    duration_minutes: int = Field(..., ge=1, le=120)
    completed: bool = False
    mood_before: Optional[MoodLevel] = None
    mood_after: Optional[MoodLevel] = None
    notes: Optional[str] = Field(None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class WellnessGoal(BaseModel):
    """Wellness goal tracking."""
    id: str = Field(..., description="Unique goal ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: ProblemCategory
    target_date: Optional[date] = None
    completed: bool = False
    progress_percentage: int = Field(0, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# Request/Response models
class CreateMoodEntryRequest(BaseModel):
    """Request to create mood entry."""
    mood_level: MoodLevel
    emotion_tags: List[EmotionTag] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=500)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    energy_level: Optional[int] = Field(None, ge=1, le=10)


class CreateJournalEntryRequest(BaseModel):
    """Request to create journal entry."""
    title: Optional[str] = Field(None, max_length=100)
    content: str = Field(..., min_length=1, max_length=5000)
    mood_before: Optional[MoodLevel] = None
    tags: List[str] = Field(default_factory=list)
    is_private: bool = True


class StartMeditationRequest(BaseModel):
    """Request to start meditation session."""
    type: MeditationType
    duration_minutes: int = Field(..., ge=1, le=120)
    mood_before: Optional[MoodLevel] = None


class CompleteMeditationRequest(BaseModel):
    """Request to complete meditation session."""
    mood_after: Optional[MoodLevel] = None
    notes: Optional[str] = Field(None, max_length=500)


class WellnessInsightRequest(BaseModel):
    """Request for wellness insights."""
    days_back: int = Field(30, ge=7, le=365)
    include_mood: bool = True
    include_journal: bool = True
    include_meditation: bool = True


class WellnessInsightResponse(BaseModel):
    """Wellness insights response."""
    period_start: date
    period_end: date
    mood_trends: Optional[Dict[str, Any]] = None
    journal_themes: Optional[List[str]] = None
    meditation_stats: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# Voice conversation models for Live API
class VoiceSessionState(str, Enum):
    """Voice session states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    TALKING = "talking"
    LISTENING = "listening"
    PROCESSING = "processing"
    ENDED = "ended"
    ERROR = "error"


class VoiceSession(BaseModel):
    """Voice conversation session using Gemini Live API."""
    session_id: str = Field(..., description="Unique voice session ID")
    user_id: str = Field(..., description="User ID")
    problem_category: Optional[ProblemCategory] = None
    state: VoiceSessionState = VoiceSessionState.CONNECTING
    voice_option: str = "Puck"  # Voice preference
    language: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    connected_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    total_duration_seconds: Optional[int] = None
    transcript: List[Dict[str, str]] = Field(default_factory=list)  # {"role": "user/assistant", "text": "...", "timestamp": "..."}
    metadata: Optional[Dict[str, Any]] = None


class VoiceSessionRequest(BaseModel):
    """Request to start a voice session."""
    problem_category: Optional[ProblemCategory] = None
    voice_option: str = "Puck"
    language: str = "en"


class VoiceSessionResponse(BaseModel):
    """Response when starting a voice session."""
    session_id: str
    state: VoiceSessionState
    websocket_url: str
    created_at: datetime


class VoiceInterruptionEvent(BaseModel):
    """Event when voice is interrupted."""
    session_id: str
    interrupted_at: datetime
    reason: str = "user_speech_detected"


class VoiceTranscriptEvent(BaseModel):
    """Real-time transcript event."""
    session_id: str
    role: str  # "user" or "assistant"
    text: str
    timestamp: datetime
    is_partial: bool = False  # For streaming transcription


# Additional missing classes that are imported in __init__.py
class UpdateMoodEntryRequest(BaseModel):
    """Request to update mood entry."""
    mood_level: Optional[MoodLevel] = None
    emotion_tags: Optional[List[EmotionTag]] = None
    notes: Optional[str] = Field(None, max_length=500)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    energy_level: Optional[int] = Field(None, ge=1, le=10)


class UpdateJournalEntryRequest(BaseModel):
    """Request to update journal entry."""
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    mood_before: Optional[MoodLevel] = None
    mood_after: Optional[MoodLevel] = None
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None


class MoodAnalysis(BaseModel):
    """Analysis of mood patterns."""
    user_id: str
    period_start: date
    period_end: date
    average_mood: float
    mood_trend: str  # "improving", "declining", "stable"
    most_common_emotions: List[str]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class GenerateMeditationRequest(BaseModel):
    """Request to generate meditation content."""
    type: MeditationType
    duration_minutes: int = Field(..., ge=1, le=120)
    problem_category: Optional[ProblemCategory] = None
    user_preferences: Optional[Dict[str, Any]] = None


class MeditationResponse(BaseModel):
    """Response with meditation content."""
    id: str
    type: MeditationType
    title: str
    script: str
    duration_minutes: int
    instructions: List[str]
    background_music_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WellnessInsight(BaseModel):
    """Individual wellness insight."""
    insight_type: str
    title: str
    description: str
    data_points: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class WellnessDashboard(BaseModel):
    """Complete wellness dashboard data."""
    user_id: str
    period_start: date
    period_end: date
    mood_summary: Optional[Dict[str, Any]] = None
    journal_summary: Optional[Dict[str, Any]] = None
    meditation_summary: Optional[Dict[str, Any]] = None
    insights: List[WellnessInsight] = Field(default_factory=list)
    goals_progress: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

