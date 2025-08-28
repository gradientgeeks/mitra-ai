"""
Pydantic models for wellness-related data structures.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


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
    ANXIETY_RELIEF = "anxiety_relief"
    FOCUS = "focus"


class JournalType(str, Enum):
    """Types of journal entries."""
    FREE_FORM = "free_form"
    GUIDED = "guided"
    GRATITUDE = "gratitude"
    REFLECTION = "reflection"
    GOAL_SETTING = "goal_setting"


class MoodEntry(BaseModel):
    """Daily mood tracking entry."""
    id: str
    user_id: str
    date: date
    mood_level: MoodLevel
    emotion_tags: List[EmotionTag] = []
    notes: Optional[str] = None
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    created_at: datetime
    updated_at: datetime


class CreateMoodEntryRequest(BaseModel):
    """Request to create a mood entry."""
    mood_level: MoodLevel
    emotion_tags: Optional[List[EmotionTag]] = []
    notes: Optional[str] = Field(None, max_length=500)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)


class UpdateMoodEntryRequest(BaseModel):
    """Request to update a mood entry."""
    mood_level: Optional[MoodLevel] = None
    emotion_tags: Optional[List[EmotionTag]] = None
    notes: Optional[str] = Field(None, max_length=500)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)


class MoodAnalysis(BaseModel):
    """Analysis of mood patterns."""
    period_start: date
    period_end: date
    average_mood: float
    mood_trend: str  # "improving", "declining", "stable"
    common_emotions: List[EmotionTag]
    insights: List[str]
    recommendations: List[str]


class JournalEntry(BaseModel):
    """Journal entry."""
    id: str
    user_id: str
    type: JournalType
    title: Optional[str] = None
    content: str
    mood_before: Optional[MoodLevel] = None
    mood_after: Optional[MoodLevel] = None
    emotion_tags: List[EmotionTag] = []
    is_private: bool = True
    created_at: datetime
    updated_at: datetime


class CreateJournalEntryRequest(BaseModel):
    """Request to create a journal entry."""
    type: JournalType = JournalType.FREE_FORM
    title: Optional[str] = Field(None, max_length=100)
    content: str = Field(..., min_length=1, max_length=5000)
    mood_before: Optional[MoodLevel] = None
    emotion_tags: Optional[List[EmotionTag]] = []


class UpdateJournalEntryRequest(BaseModel):
    """Request to update a journal entry."""
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    mood_after: Optional[MoodLevel] = None
    emotion_tags: Optional[List[EmotionTag]] = None


class MeditationSession(BaseModel):
    """Meditation session record."""
    id: str
    user_id: str
    type: MeditationType
    title: str
    duration_minutes: int
    audio_url: Optional[str] = None
    script: Optional[str] = None
    completed: bool = False
    mood_before: Optional[MoodLevel] = None
    mood_after: Optional[MoodLevel] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class GenerateMeditationRequest(BaseModel):
    """Request to generate a custom meditation."""
    type: MeditationType
    duration_minutes: int = Field(..., ge=1, le=60)
    focus_area: Optional[str] = Field(None, max_length=200)
    current_mood: Optional[MoodLevel] = None
    voice: Optional[str] = "Puck"
    format: str = Field(default="audio", pattern="^(audio|text)$")


class MeditationResponse(BaseModel):
    """Response with generated meditation."""
    session_id: str
    title: str
    type: MeditationType
    duration_minutes: int
    audio_data: Optional[bytes] = None
    script: Optional[str] = None
    instructions: List[str]
    created_at: datetime


class WellnessInsight(BaseModel):
    """Wellness insight and recommendation."""
    id: str
    user_id: str
    type: str  # "mood_pattern", "journal_reflection", "meditation_suggestion"
    title: str
    content: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    action_items: List[str] = []
    expires_at: Optional[datetime] = None
    created_at: datetime
    viewed: bool = False


class WellnessDashboard(BaseModel):
    """Wellness dashboard data."""
    user_id: str
    current_mood: Optional[MoodLevel] = None
    mood_trend: Optional[str] = None
    recent_mood_entries: List[MoodEntry] = []
    recent_journal_entries: List[JournalEntry] = []
    recent_meditations: List[MeditationSession] = []
    insights: List[WellnessInsight] = []
    streak_days: int = 0
    total_sessions: int = 0