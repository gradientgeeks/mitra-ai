"""
Base Gemini service providing common functionality for all Gemini-based services.
"""

import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from PIL import Image
import io

from core.config import settings
from models.chat import ChatMessage, MessageRole, MessageType
from models.common import GenerationConfig, GroundingSource
from models.user import UserProfile, AgeGroup, Gender, ProblemCategory

logger = logging.getLogger(__name__)


class BaseGeminiService:
    """Base service for common Gemini AI functionality."""
    
    def __init__(self):
        """Initialize Gemini client."""
        self.client = genai.Client(api_key=settings.google_api_key)
        
        # Base system instruction for Mitra AI
        self.base_system_instruction = """
        You are {mitra_name} (मित्र), a compassionate and empathetic AI companion designed to support 
        the mental wellness of young people in India. Your role is to:

        1. Be a non-judgmental, supportive friend who listens without criticism
        2. Provide culturally sensitive support that respects Indian values and traditions
        3. Offer practical coping strategies and wellness techniques
        4. Guide users toward professional help when appropriate
        5. Maintain strict confidentiality and user privacy

        Core Principles:
        - Always prioritize user safety and well-being
        - Be warm, empathetic, and encouraging
        - Use simple, clear language that's accessible to young people
        - Respect cultural and religious diversity in India
        - Never provide medical diagnoses or replace professional therapy
        - Gently redirect when conversations become inappropriate

        Communication Style:
        - Be conversational and friendly, like a caring friend
        - Use encouraging phrases and validate emotions
        - Ask thoughtful follow-up questions to understand better
        - Offer hope and perspective when appropriate
        - Use examples and stories when helpful

        Remember: You're here to support, not to solve all problems. Sometimes the best 
        help is just listening and being present.
        """

    def get_personalized_system_instruction(
        self, 
        user_profile: Optional[UserProfile] = None, 
        problem_category: Optional[ProblemCategory] = None
    ) -> str:
        """Get personalized system instruction based on user profile and context."""
        
        # Default values
        mitra_name = "Mitra"
        age_context = ""
        problem_context = ""
        
        if user_profile:
            # Use personalized Mitra name
            if user_profile.preferences and user_profile.preferences.mitra_name:
                mitra_name = user_profile.preferences.mitra_name
            
            # Add age-appropriate context
            if user_profile.age_group:
                age_contexts = {
                    AgeGroup.TEEN: """
                    User Context: You're speaking with a teenager (13-17 years). Be especially:
                    - Understanding of academic pressure and peer relationships
                    - Aware of identity formation challenges
                    - Supportive of their developing independence
                    - Sensitive to family dynamics and expectations
                    - Use relatable examples from school, friendships, and social media
                    """,
                    AgeGroup.YOUNG_ADULT: """
                    User Context: You're speaking with a young adult (18-24 years). Focus on:
                    - Career and education decisions
                    - Relationship and independence issues
                    - Financial stress and future planning
                    - Transitioning to adult responsibilities
                    - Use examples relevant to college, jobs, and life transitions
                    """,
                    AgeGroup.ADULT: """
                    User Context: You're speaking with an adult (25-34 years). Address:
                    - Work-life balance and career growth
                    - Relationship and family planning
                    - Financial stability and responsibilities
                    - Personal goals and life direction
                    - Use examples from professional and personal life
                    """,
                    AgeGroup.MATURE_ADULT: """
                    User Context: You're speaking with a mature adult (35+ years). Consider:
                    - Family and parenting responsibilities
                    - Career advancement and stability
                    - Health and aging concerns
                    - Legacy and life satisfaction
                    - Use examples from established life experiences
                    """
                }
                age_context = age_contexts.get(user_profile.age_group, "")
        
        # Add problem-specific context
        if problem_category:
            problem_contexts = {
                ProblemCategory.STRESS_ANXIETY: """
                Session Focus: The user is dealing with stress and anxiety. Provide:
                - Immediate stress relief techniques (breathing, grounding)
                - Long-term anxiety management strategies
                - Understanding of stress triggers and responses
                - Gentle, calming communication style
                """,
                ProblemCategory.DEPRESSION_SADNESS: """
                Session Focus: The user is experiencing depression or sadness. Offer:
                - Validation of their feelings without minimizing
                - Small, achievable steps toward improvement
                - Encouragement to seek professional help if needed
                - Hope and perspective while being realistic
                """,
                ProblemCategory.RELATIONSHIP_ISSUES: """
                Session Focus: The user has relationship concerns. Help with:
                - Communication skills and conflict resolution
                - Boundary setting and self-respect
                - Understanding relationship dynamics
                - Cultural considerations for Indian relationships
                """,
                ProblemCategory.ACADEMIC_PRESSURE: """
                Session Focus: The user faces academic pressure. Address:
                - Study techniques and time management
                - Dealing with performance anxiety
                - Balancing expectations with well-being
                - Understanding the Indian education system pressures
                """,
                ProblemCategory.FAMILY_PROBLEMS: """
                Session Focus: The user has family issues. Consider:
                - Navigating family expectations and traditions
                - Intergenerational communication gaps
                - Balancing personal goals with family duties
                - Respect for cultural values while asserting needs
                """
            }
            problem_context = problem_contexts.get(problem_category, "")
        
        # Combine all instruction parts
        full_instruction = self.base_system_instruction.format(mitra_name=mitra_name)
        if age_context:
            full_instruction += "\n\n" + age_context
        if problem_context:
            full_instruction += "\n\n" + problem_context
            
        return full_instruction

    def _convert_messages_to_gemini_format(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Convert ChatMessage objects to Gemini API format."""
        gemini_messages = []
        
        for message in messages:
            role = "user" if message.role == MessageRole.USER else "model"
            
            # Convert content based on type
            if message.type == MessageType.TEXT and message.content.text:
                gemini_messages.append({
                    "role": role,
                    "parts": [{"text": message.content.text}]
                })
            elif message.type == MessageType.IMAGE and message.content.image_data:
                # Convert image data to PIL Image
                image = Image.open(io.BytesIO(message.content.image_data))
                parts = []
                if message.content.text:
                    parts.append({"text": message.content.text})
                parts.append(image)
                gemini_messages.append({
                    "role": role,
                    "parts": parts
                })
        
        return gemini_messages

    def _convert_messages_to_text(self, messages: List[ChatMessage]) -> str:
        """Convert messages to plain text format."""
        text_parts = []
        
        for message in messages:
            role_prefix = "User" if message.role == MessageRole.USER else "Assistant"
            if message.content.text:
                text_parts.append(f"{role_prefix}: {message.content.text}")
        
        return "\n\n".join(text_parts)

    def _prepare_generation_config(self, config: Optional[GenerationConfig]) -> Dict[str, Any]:
        """Prepare generation configuration for Gemini API."""
        gen_config = {}
        
        if config:
            if config.temperature is not None:
                gen_config["temperature"] = config.temperature
            if config.max_tokens is not None:
                gen_config["max_output_tokens"] = config.max_tokens
            if config.top_p is not None:
                gen_config["top_p"] = config.top_p
            if config.top_k is not None:
                gen_config["top_k"] = config.top_k
            if config.thinking_budget is not None:
                gen_config["thinking_config"] = types.ThinkingConfig(
                    thinking_budget=config.thinking_budget
                )
        
        return gen_config

    def _extract_grounding_sources(self, grounding_metadata) -> List[GroundingSource]:
        """Extract grounding sources from Gemini response metadata."""
        sources = []
        
        if hasattr(grounding_metadata, 'grounding_chunks'):
            for chunk in grounding_metadata.grounding_chunks:
                if hasattr(chunk, 'web'):
                    sources.append(GroundingSource(
                        title=chunk.web.title,
                        url=chunk.web.uri,
                        snippet=""  # Extract snippet if available
                    ))
        
        return sources