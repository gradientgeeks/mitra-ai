"""
Wellness-specific service for Mitra AI.
Handles meditation scripts, wellness insights, and mental health content.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from google.genai import types

from .base_gemini_service import BaseGeminiService
from .text_generation_service import TextGenerationService
from core.config import settings

logger = logging.getLogger(__name__)


class WellnessService(BaseGeminiService):
    """Service for wellness-specific functionality."""

    def __init__(self):
        """Initialize with base functionality and text generation service."""
        super().__init__()
        self.text_service = TextGenerationService()

    async def generate_meditation_script(
        self,
        meditation_type: str,
        duration_minutes: int,
        focus_area: Optional[str] = None
    ) -> str:
        """
        Generate a custom meditation script.
        
        Args:
            meditation_type: Type of meditation
            duration_minutes: Duration in minutes
            focus_area: Specific focus area if any
            
        Returns:
            Generated meditation script
        """
        try:
            prompt = f"""
            Create a {duration_minutes}-minute {meditation_type} meditation script for Indian youth.
            
            Requirements:
            - Appropriate for young people dealing with academic and social pressure
            - Culturally sensitive and inclusive
            - Simple, clear instructions
            - Calming and supportive tone
            - Include timing cues for a {duration_minutes}-minute session
            
            {f"Focus specifically on: {focus_area}" if focus_area else ""}
            
            Format as a gentle, step-by-step guide with timing markers.
            """
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.gemini_text_model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating meditation script: {e}")
            raise

    async def generate_wellness_insight(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized wellness insights based on user data.
        
        Args:
            user_data: User's wellness data (mood, journal entries, etc.)
            
        Returns:
            Structured wellness insight
        """
        try:
            prompt = f"""
            Based on this user's wellness data, provide personalized insights and recommendations:
            
            {user_data}
            
            Provide:
            1. Key patterns you notice
            2. Specific, actionable recommendations
            3. Encouraging observations
            4. Gentle suggestions for improvement
            
            Keep it positive, supportive, and culturally appropriate for Indian youth.
            """
            
            schema = {
                "type": "object",
                "properties": {
                    "patterns": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "positive_observations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "improvement_suggestions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "overall_assessment": {"type": "string"}
                },
                "required": ["patterns", "recommendations", "positive_observations"]
            }
            
            return await self.text_service.generate_structured_content(prompt, schema)
            
        except Exception as e:
            logger.error(f"Error generating wellness insight: {e}")
            raise

    async def generate_coping_strategy(
        self,
        emotion: str,
        situation: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized coping strategies.
        
        Args:
            emotion: Current emotion (anxiety, stress, sadness, etc.)
            situation: Current situation description
            user_preferences: User preferences and cultural context
            
        Returns:
            Structured coping strategy recommendations
        """
        try:
            preferences_text = ""
            if user_preferences:
                preferences_text = f"User preferences and context: {user_preferences}"
            
            prompt = f"""
            Generate culturally appropriate coping strategies for an Indian youth experiencing {emotion} 
            in this situation: {situation}
            
            {preferences_text}
            
            Provide immediate, practical strategies that are:
            - Culturally sensitive to Indian values
            - Age-appropriate for young people
            - Evidence-based but accessible
            - Can be done without special equipment
            - Respectful of family and social dynamics
            """
            
            schema = {
                "type": "object",
                "properties": {
                    "immediate_strategies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Quick techniques to use right now"
                    },
                    "breathing_exercises": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Simple breathing techniques"
                    },
                    "cognitive_techniques": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Thought reframing strategies"
                    },
                    "physical_activities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Gentle physical activities"
                    },
                    "social_support": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ways to connect with others appropriately"
                    },
                    "encouragement": {"type": "string"}
                },
                "required": ["immediate_strategies", "encouragement"]
            }
            
            return await self.text_service.generate_structured_content(prompt, schema)
            
        except Exception as e:
            logger.error(f"Error generating coping strategy: {e}")
            raise

    async def generate_mood_check_in(
        self,
        previous_mood_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized mood check-in questions and prompts.
        
        Args:
            previous_mood_data: Previous mood tracking data if available
            
        Returns:
            Structured mood check-in content
        """
        try:
            history_text = ""
            if previous_mood_data:
                history_text = f"Previous mood data: {previous_mood_data}"
            
            prompt = f"""
            Create a thoughtful mood check-in for an Indian youth that feels supportive and engaging.
            
            {history_text}
            
            Generate:
            - Gentle, caring questions to assess current mood
            - Culturally appropriate reflection prompts
            - Encouraging statements
            - Follow-up questions based on responses
            
            Keep it warm, non-clinical, and like a caring friend checking in.
            """
            
            schema = {
                "type": "object",
                "properties": {
                    "opening_message": {"type": "string"},
                    "mood_questions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "reflection_prompts": {
                        "type": "array", 
                        "items": {"type": "string"}
                    },
                    "encouragement": {"type": "string"},
                    "follow_up_options": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["opening_message", "mood_questions", "encouragement"]
            }
            
            return await self.text_service.generate_structured_content(prompt, schema)
            
        except Exception as e:
            logger.error(f"Error generating mood check-in: {e}")
            raise