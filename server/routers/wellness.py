"""
Wellness router for mood tracking, journaling, and meditation features.
"""

import logging
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import Response

from models.wellness import (
    MoodEntry, CreateMoodEntryRequest, UpdateMoodEntryRequest, MoodAnalysis,
    JournalEntry, CreateJournalEntryRequest, UpdateJournalEntryRequest,
    MeditationSession, GenerateMeditationRequest, MeditationResponse,
    WellnessInsight, WellnessDashboard, MoodLevel, EmotionTag, MeditationType
)
from models.common import APIResponse, ErrorResponse, ErrorType
from services.gemini_service import GeminiService
from repository.firestore_repository import FirestoreRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
def get_gemini_service() -> GeminiService:
    return GeminiService()

def get_repository() -> FirestoreRepository:
    return FirestoreRepository()

async def get_current_user(authorization: str = Header(None)) -> str:
    """Extract user ID from authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    return f"user_{hash(token) % 10000}"  # Mock user ID


# Mood tracking endpoints
@router.post("/mood", response_model=MoodEntry)
async def create_mood_entry(
    request: CreateMoodEntryRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Create a new mood entry for the current user."""
    try:
        mood_entry = MoodEntry(
            id=str(uuid.uuid4()),
            user_id=current_user,
            date=date.today(),
            mood_level=request.mood_level,
            emotion_tags=request.emotion_tags or [],
            notes=request.notes,
            energy_level=request.energy_level,
            sleep_quality=request.sleep_quality,
            stress_level=request.stress_level,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        success = await repository.create_mood_entry(mood_entry)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save mood entry")
        
        # Update user's last mood entry timestamp
        await repository.update_user(current_user, {
            "last_mood_entry": datetime.utcnow()
        })
        
        return mood_entry
        
    except Exception as e:
        logger.error(f"Error creating mood entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to create mood entry")


@router.get("/mood", response_model=List[MoodEntry])
async def get_mood_entries(
    limit: int = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get mood entries for the current user."""
    try:
        mood_entries = await repository.get_mood_entries(
            current_user,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        return mood_entries
        
    except Exception as e:
        logger.error(f"Error getting mood entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get mood entries")


@router.put("/mood/{entry_id}", response_model=MoodEntry)
async def update_mood_entry(
    entry_id: str,
    request: UpdateMoodEntryRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Update an existing mood entry."""
    try:
        # In production, first get the existing entry and verify ownership
        # For now, create updated entry
        mood_entry = MoodEntry(
            id=entry_id,
            user_id=current_user,
            date=date.today(),  # In production, preserve original date
            mood_level=request.mood_level or MoodLevel.NEUTRAL,
            emotion_tags=request.emotion_tags or [],
            notes=request.notes,
            energy_level=request.energy_level,
            sleep_quality=request.sleep_quality,
            stress_level=request.stress_level,
            created_at=datetime.utcnow(),  # In production, preserve original
            updated_at=datetime.utcnow()
        )
        
        success = await repository.update_mood_entry(current_user, mood_entry)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update mood entry")
        
        return mood_entry
        
    except Exception as e:
        logger.error(f"Error updating mood entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to update mood entry")


@router.get("/mood/analysis", response_model=MoodAnalysis)
async def get_mood_analysis(
    days: int = 30,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """Get mood pattern analysis and insights."""
    try:
        # Get recent mood entries
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        mood_entries = await repository.get_mood_entries(
            current_user,
            limit=days,
            start_date=start_date,
            end_date=end_date
        )
        
        if not mood_entries:
            return MoodAnalysis(
                period_start=start_date,
                period_end=end_date,
                average_mood=5.0,
                mood_trend="stable",
                common_emotions=[],
                insights=["Not enough data for analysis. Keep tracking your mood!"],
                recommendations=["Track your mood daily for better insights"]
            )
        
        # Calculate basic statistics
        mood_values = [entry.mood_level.value for entry in mood_entries]
        average_mood = sum(mood_values) / len(mood_values)
        
        # Determine trend (simple approach)
        if len(mood_values) >= 7:
            recent_avg = sum(mood_values[-7:]) / 7
            older_avg = sum(mood_values[:-7]) / len(mood_values[:-7])
            
            if recent_avg > older_avg + 0.5:
                trend = "improving"
            elif recent_avg < older_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Get common emotions
        all_emotions = []
        for entry in mood_entries:
            all_emotions.extend(entry.emotion_tags)
        
        emotion_counts = {}
        for emotion in all_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        common_emotions = sorted(emotion_counts.keys(), 
                               key=lambda x: emotion_counts[x], 
                               reverse=True)[:5]
        
        # Generate AI insights
        mood_data = {
            "average_mood": average_mood,
            "trend": trend,
            "common_emotions": [e.value for e in common_emotions],
            "mood_entries_count": len(mood_entries),
            "period_days": days
        }
        
        insights_data = await gemini_service.generate_wellness_insight(mood_data)
        
        return MoodAnalysis(
            period_start=start_date,
            period_end=end_date,
            average_mood=average_mood,
            mood_trend=trend,
            common_emotions=common_emotions,
            insights=insights_data.get("patterns", []),
            recommendations=insights_data.get("recommendations", [])
        )
        
    except Exception as e:
        logger.error(f"Error generating mood analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate mood analysis")


# Journaling endpoints
@router.post("/journal", response_model=JournalEntry)
async def create_journal_entry(
    request: CreateJournalEntryRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Create a new journal entry."""
    try:
        journal_entry = JournalEntry(
            id=str(uuid.uuid4()),
            user_id=current_user,
            type=request.type,
            title=request.title,
            content=request.content,
            mood_before=request.mood_before,
            emotion_tags=request.emotion_tags or [],
            is_private=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        success = await repository.create_journal_entry(journal_entry)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save journal entry")
        
        return journal_entry
        
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to create journal entry")


@router.get("/journal", response_model=List[JournalEntry])
async def get_journal_entries(
    limit: int = 20,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get journal entries for the current user."""
    try:
        journal_entries = await repository.get_journal_entries(current_user, limit)
        return journal_entries
        
    except Exception as e:
        logger.error(f"Error getting journal entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get journal entries")


@router.put("/journal/{entry_id}", response_model=JournalEntry)
async def update_journal_entry(
    entry_id: str,
    request: UpdateJournalEntryRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Update an existing journal entry."""
    try:
        # In production, first get and verify ownership
        updated_entry = JournalEntry(
            id=entry_id,
            user_id=current_user,
            type="free_form",  # In production, preserve original type
            title=request.title,
            content=request.content or "",
            mood_after=request.mood_after,
            emotion_tags=request.emotion_tags or [],
            is_private=True,
            created_at=datetime.utcnow(),  # In production, preserve original
            updated_at=datetime.utcnow()
        )
        
        success = await repository.update_journal_entry(current_user, updated_entry)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update journal entry")
        
        return updated_entry
        
    except Exception as e:
        logger.error(f"Error updating journal entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to update journal entry")


@router.post("/journal/guided-prompt")
async def get_guided_journal_prompt(
    current_user: str = Depends(get_current_user),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """Get a guided journaling prompt based on current wellness state."""
    try:
        # Generate a thoughtful journaling prompt
        prompt = """
        Generate a gentle, supportive journaling prompt for a young person in India 
        who is working on their mental wellness. The prompt should:
        
        1. Be culturally sensitive and inclusive
        2. Encourage self-reflection without being overwhelming
        3. Be appropriate for someone dealing with academic or social pressure
        4. Include 3-4 specific questions or prompts
        5. Be encouraging and non-judgmental
        
        Format the response as a friendly, supportive message.
        """
        
        response_text, _, _ = await gemini_service.generate_text_response(
            [],  # No conversation history for prompts
            include_grounding=False
        )
        
        return {"prompt": response_text}
        
    except Exception as e:
        logger.error(f"Error generating journal prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate journal prompt")


# Meditation endpoints
@router.post("/meditation/generate", response_model=MeditationResponse)
async def generate_custom_meditation(
    request: GenerateMeditationRequest,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """Generate a custom meditation session."""
    try:
        # Generate meditation script
        meditation_script = await gemini_service.generate_meditation_script(
            request.type.value,
            request.duration_minutes,
            request.focus_area
        )
        
        # Create meditation session record
        meditation_session = MeditationSession(
            id=str(uuid.uuid4()),
            user_id=current_user,
            type=request.type,
            title=f"{request.duration_minutes}-minute {request.type.value.replace('_', ' ').title()}",
            duration_minutes=request.duration_minutes,
            script=meditation_script,
            completed=False,
            mood_before=request.current_mood,
            created_at=datetime.utcnow()
        )
        
        success = await repository.create_meditation_session(meditation_session)
        if not success:
            logger.warning("Failed to save meditation session")
        
        # Generate audio if requested
        audio_data = None
        if request.format == "audio":
            try:
                # In production, convert script to audio using TTS
                # For now, return None
                pass
            except Exception as e:
                logger.warning(f"Failed to generate audio: {e}")
        
        # Generate instructions
        instructions = [
            "Find a quiet, comfortable space",
            "Sit or lie down in a relaxed position",
            "Close your eyes or soften your gaze",
            "Follow along with the guided meditation",
            "Don't worry if your mind wanders - it's normal!"
        ]
        
        return MeditationResponse(
            session_id=meditation_session.id,
            title=meditation_session.title,
            type=request.type,
            duration_minutes=request.duration_minutes,
            audio_data=audio_data,
            script=meditation_script,
            instructions=instructions,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error generating meditation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate meditation")


@router.post("/meditation/{session_id}/complete")
async def complete_meditation_session(
    session_id: str,
    mood_after: Optional[MoodLevel] = None,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Mark a meditation session as completed."""
    try:
        success = await repository.complete_meditation_session(
            current_user,
            session_id,
            mood_after.value if mood_after else None
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Meditation session not found")
        
        return {"message": "Meditation session completed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing meditation session: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete meditation session")


@router.get("/meditation/sessions", response_model=List[MeditationSession])
async def get_meditation_sessions(
    limit: int = 20,
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get user's meditation sessions."""
    try:
        # In production, implement this query
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting meditation sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get meditation sessions")


# Dashboard endpoint
@router.get("/dashboard", response_model=WellnessDashboard)
async def get_wellness_dashboard(
    current_user: str = Depends(get_current_user),
    repository: FirestoreRepository = Depends(get_repository)
):
    """Get comprehensive wellness dashboard data."""
    try:
        # Get recent data
        recent_moods = await repository.get_mood_entries(current_user, limit=7)
        recent_journals = await repository.get_journal_entries(current_user, limit=5)
        
        # Calculate current mood and trend
        current_mood = None
        mood_trend = None
        
        if recent_moods:
            current_mood = recent_moods[0].mood_level  # Most recent
            
            if len(recent_moods) >= 3:
                recent_avg = sum(m.mood_level.value for m in recent_moods[:3]) / 3
                older_avg = sum(m.mood_level.value for m in recent_moods[3:]) / max(len(recent_moods[3:]), 1)
                
                if recent_avg > older_avg + 0.5:
                    mood_trend = "improving"
                elif recent_avg < older_avg - 0.5:
                    mood_trend = "declining"
                else:
                    mood_trend = "stable"
        
        # Get user stats
        stats = await repository.get_user_stats(current_user)
        
        return WellnessDashboard(
            user_id=current_user,
            current_mood=current_mood,
            mood_trend=mood_trend,
            recent_mood_entries=recent_moods,
            recent_journal_entries=recent_journals,
            recent_meditations=[],  # Would be populated in production
            insights=[],  # Would be populated with AI insights
            streak_days=stats.get("current_streak", 0),
            total_sessions=stats.get("total_sessions", 0)
        )
        
    except Exception as e:
        logger.error(f"Error getting wellness dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get wellness dashboard")