"""
Wellness-specific service for Mitra AI.
Handles meditation scripts, wellness insights, and mental health content.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List

from google.genai import types

from .base_gemini_service import BaseGeminiService
from .text_generation_service import TextGenerationService
from core.config import settings
from models.user import UserProfile, AgeGroup, ProblemCategory
from models.chat import ResourceType, GeneratedResource

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

    async def generate_personalized_content(
        self,
        user_profile: UserProfile,
        content_type: str,
        specific_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate age-appropriate and personalized wellness content.
        
        Args:
            user_profile: User's profile with age and preferences
            content_type: Type of content to generate
            specific_request: Specific user request
            
        Returns:
            Personalized wellness content
        """
        try:
            # Get personalized system instruction
            system_instruction = self.get_personalized_system_instruction(user_profile)
            
            # Age-specific content guidelines
            age_guidelines = {
                AgeGroup.TEEN: "Focus on school stress, peer pressure, identity questions, family expectations",
                AgeGroup.YOUNG_ADULT: "Address career decisions, independence, relationships, future planning",
                AgeGroup.ADULT: "Cover work-life balance, responsibilities, relationship management",
                AgeGroup.MATURE_ADULT: "Include family leadership, career stability, health awareness"
            }
            
            age_context = age_guidelines.get(user_profile.age_group, "")
            mitra_name = user_profile.preferences.mitra_name if user_profile.preferences else "Mitra"
            
            prompt = f"""
            As {mitra_name}, create personalized {content_type} content for this user.
            
            User Context:
            - Age Group: {user_profile.age_group}
            - Specific Focus: {age_context}
            - Mitra Name: {mitra_name}
            
            {f"Specific Request: {specific_request}" if specific_request else ""}
            
            Create content that is:
            - Age-appropriate and culturally sensitive
            - Relevant to their life stage
            - Warm and supportive
            - Practical and actionable
            """
            
            response = await self.client.models.generate_content(
                model=settings.gemini_model,
                contents=[prompt],
                config={"system_instruction": system_instruction}
            )
            
            return {
                "content": response.text,
                "age_group": user_profile.age_group,
                "mitra_name": mitra_name,
                "content_type": content_type
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized content: {e}")
            raise

    async def generate_session_resources(
        self,
        problem_category: ProblemCategory,
        user_profile: UserProfile,
        session_context: str,
        resource_types: Optional[List[ResourceType]] = None
    ) -> List[GeneratedResource]:
        """
        Generate helpful resources based on session content and problem category.
        
        Args:
            problem_category: The main problem discussed in session
            user_profile: User's profile for personalization
            session_context: Summary of session conversation
            resource_types: Specific types of resources to generate
            
        Returns:
            List of generated resources
        """
        try:
            if not resource_types:
                # Default resources based on problem category
                resource_mapping = {
                    ProblemCategory.STRESS_ANXIETY: [ResourceType.BREATHING_EXERCISE, ResourceType.MEDITATION, ResourceType.COPING_STRATEGIES],
                    ProblemCategory.DEPRESSION_SADNESS: [ResourceType.AFFIRMATIONS, ResourceType.COPING_STRATEGIES, ResourceType.ARTICLES],
                    ProblemCategory.RELATIONSHIP_ISSUES: [ResourceType.COPING_STRATEGIES, ResourceType.ARTICLES, ResourceType.WORKSHEETS],
                    ProblemCategory.ACADEMIC_PRESSURE: [ResourceType.COPING_STRATEGIES, ResourceType.MEDITATION, ResourceType.WORKSHEETS],
                    ProblemCategory.FAMILY_PROBLEMS: [ResourceType.COPING_STRATEGIES, ResourceType.AFFIRMATIONS, ResourceType.ARTICLES]
                }
                resource_types = resource_mapping.get(problem_category, [ResourceType.COPING_STRATEGIES, ResourceType.AFFIRMATIONS])
            
            resources = []
            system_instruction = self.get_personalized_system_instruction(user_profile, problem_category)
            mitra_name = user_profile.preferences.mitra_name if user_profile.preferences else "Mitra"
            
            for resource_type in resource_types[:3]:  # Limit to 3 resources
                resource = await self._generate_single_resource(
                    resource_type, problem_category, user_profile, session_context, system_instruction, mitra_name
                )
                if resource:
                    resources.append(resource)
                    
            return resources
            
        except Exception as e:
            logger.error(f"Error generating session resources: {e}")
            raise

    async def _generate_single_resource(
        self,
        resource_type: ResourceType,
        problem_category: ProblemCategory,
        user_profile: UserProfile,
        session_context: str,
        system_instruction: str,
        mitra_name: str
    ) -> Optional[GeneratedResource]:
        """Generate a single resource of specified type."""
        try:
            from datetime import datetime
            import uuid
            
            # Resource-specific prompts
            prompts = {
                ResourceType.MEDITATION: f"""
                Create a guided meditation script specifically for {problem_category.value.replace('_', ' ')}.
                Duration: 5-10 minutes
                Target: {user_profile.age_group.value.replace('_', ' ')} age group
                Context: {session_context}
                
                Make it practical, soothing, and culturally appropriate for Indian users.
                """,
                
                ResourceType.BREATHING_EXERCISE: f"""
                Design a breathing exercise for {problem_category.value.replace('_', ' ')}.
                Duration: 3-5 minutes
                Age group: {user_profile.age_group.value.replace('_', ' ')}
                Context: {session_context}
                
                Include clear, step-by-step instructions that are easy to follow.
                """,
                
                ResourceType.COPING_STRATEGIES: f"""
                Provide 5-7 practical coping strategies for {problem_category.value.replace('_', ' ')}.
                Target: {user_profile.age_group.value.replace('_', ' ')} in Indian context
                Session context: {session_context}
                
                Make strategies actionable, culturally sensitive, and age-appropriate.
                """,
                
                ResourceType.AFFIRMATIONS: f"""
                Create 8-10 positive affirmations for someone dealing with {problem_category.value.replace('_', ' ')}.
                Age group: {user_profile.age_group.value.replace('_', ' ')}
                Context: {session_context}
                
                Make them empowering, culturally relevant, and authentic to Indian values.
                """
            }
            
            prompt = prompts.get(resource_type, "")
            if not prompt:
                return None
                
            response = await self.client.models.generate_content(
                model=settings.gemini_model,
                contents=[prompt],
                config={"system_instruction": system_instruction}
            )
            
            # Generate title and description
            title_prompt = f"Create a short, engaging title for this {resource_type.value} resource about {problem_category.value.replace('_', ' ')}"
            title_response = await self.client.models.generate_content(
                model=settings.gemini_model,
                contents=[title_prompt]
            )
            
            desc_prompt = f"Write a brief 1-2 sentence description for this {resource_type.value} resource"
            desc_response = await self.client.models.generate_content(
                model=settings.gemini_model,
                contents=[desc_prompt]
            )
            
            # Determine duration and difficulty
            duration = None
            if resource_type in [ResourceType.MEDITATION, ResourceType.BREATHING_EXERCISE]:
                duration = 5 if resource_type == ResourceType.BREATHING_EXERCISE else 8
                
            difficulty = "beginner"
            if user_profile.age_group in [AgeGroup.ADULT, AgeGroup.MATURE_ADULT]:
                difficulty = "intermediate"
            
            return GeneratedResource(
                id=str(uuid.uuid4()),
                type=resource_type,
                title=title_response.text.strip(),
                description=desc_response.text.strip(),
                content=response.text,
                duration_minutes=duration,
                difficulty_level=difficulty,
                tags=[problem_category.value, user_profile.age_group.value],
                created_at=datetime.utcnow(),
                problem_category=problem_category
            )
            
        except Exception as e:
            logger.error(f"Error generating {resource_type} resource: {e}")
            return None