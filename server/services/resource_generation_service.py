"""
Resource generation service for Mitra AI.
Generates helpful resources based on chat session analysis using MCP tools for latest documentation.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.user import ProblemCategory, UserProfile
from models.wellness import GeneratedResource, ResourceType
from services.base_gemini_service import BaseGeminiService

logger = logging.getLogger(__name__)


class ResourceGenerationService(BaseGeminiService):
    """Service for generating contextual resources based on chat analysis."""

    async def generate_session_resources(
        self,
        problem_category: ProblemCategory,
        user_profile: Optional[UserProfile],
        session_context: str,
        resource_types: Optional[List[str]] = None,
        max_resources: int = 3
    ) -> List[GeneratedResource]:
        """
        Generate helpful resources based on chat session analysis.

        Args:
            problem_category: The main problem category being discussed
            user_profile: User profile for personalization
            session_context: Context from recent messages in the session
            resource_types: Specific resource types to generate
            max_resources: Maximum number of resources to generate

        Returns:
            List of generated resources
        """
        try:
            # Define available resource types based on problem category
            if resource_types is None:
                resource_types = self._get_default_resource_types(problem_category)

            resources = []

            for resource_type in resource_types[:max_resources]:
                resource = await self._generate_specific_resource(
                    resource_type=resource_type,
                    problem_category=problem_category,
                    user_profile=user_profile,
                    session_context=session_context
                )

                if resource:
                    resources.append(resource)

            return resources

        except Exception as e:
            logger.error(f"Error generating session resources: {e}")
            return []

    def _get_default_resource_types(self, problem_category: ProblemCategory) -> List[str]:
        """Get default resource types based on problem category."""
        resource_mapping = {
            ProblemCategory.STRESS_ANXIETY: [
                "breathing_exercise",
                "coping_strategies",
                "meditation"
            ],
            ProblemCategory.DEPRESSION_SADNESS: [
                "mood_tracker_tips",
                "self_care_activities",
                "professional_resources"
            ],
            ProblemCategory.RELATIONSHIP_ISSUES: [
                "communication_techniques",
                "boundary_setting",
                "conflict_resolution"
            ],
            ProblemCategory.ACADEMIC_PRESSURE: [
                "study_techniques",
                "time_management",
                "stress_management"
            ],
            ProblemCategory.SLEEP_ISSUES: [
                "sleep_hygiene",
                "relaxation_techniques",
                "bedtime_routine"
            ],
        }

        return resource_mapping.get(problem_category, [
            "general_wellness",
            "mindfulness",
            "self_reflection"
        ])

    async def _generate_specific_resource(
        self,
        resource_type: str,
        problem_category: ProblemCategory,
        user_profile: Optional[UserProfile],
        session_context: str
    ) -> Optional[GeneratedResource]:
        """Generate a specific type of resource."""
        try:
            # Create personalized prompt based on resource type
            prompt = self._create_resource_prompt(
                resource_type=resource_type,
                problem_category=problem_category,
                user_profile=user_profile,
                session_context=session_context
            )

            # Use structured output to generate the resource
            schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "content": {"type": "string"},
                    "duration_minutes": {"type": "integer"},
                    "difficulty_level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"]
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["title", "description", "content", "difficulty_level", "tags"]
            }

            # Generate structured content using Gemini
            response = await self.generate_structured_content(prompt, schema)

            # Create GeneratedResource object
            resource = GeneratedResource(
                id=f"resource_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{resource_type}",
                type=resource_type,
                title=response["title"],
                description=response["description"],
                content=response["content"],
                duration_minutes=response.get("duration_minutes"),
                difficulty_level=response["difficulty_level"],
                tags=response["tags"],
                created_at=datetime.utcnow(),
                problem_category=problem_category
            )

            return resource

        except Exception as e:
            logger.error(f"Error generating {resource_type} resource: {e}")
            return None

    def _create_resource_prompt(
        self,
        resource_type: str,
        problem_category: ProblemCategory,
        user_profile: Optional[UserProfile],
        session_context: str
    ) -> str:
        """Create a personalized prompt for resource generation."""

        # Base context
        age_context = ""
        if user_profile and user_profile.age_group:
            age_context = f"The user is in the {user_profile.age_group.value.replace('_', ' ')} age group."

        problem_context = f"The user is dealing with {problem_category.value.replace('_', ' ')}."

        # Session context (truncated to avoid token limits)
        context_preview = session_context[:500] + "..." if len(session_context) > 500 else session_context

        # Resource-specific prompts
        resource_prompts = {
            "breathing_exercise": f"""
Create a guided breathing exercise resource for someone dealing with {problem_category.value.replace('_', ' ')}.
{age_context}
Recent conversation context: {context_preview}

The resource should include:
- A clear, easy-to-follow breathing technique
- Step-by-step instructions
- Benefits explanation
- Duration and difficulty appropriate for the user's situation
- Markdown formatted content with clear headings and bullet points

Make it culturally appropriate for Indian users and reference any relevant concepts from Indian wellness traditions if applicable.
            """,

            "coping_strategies": f"""
Generate practical coping strategies for {problem_category.value.replace('_', ' ')}.
{age_context}
Based on the conversation: {context_preview}

Include:
- 3-5 specific, actionable coping techniques
- When and how to use each strategy
- Cultural considerations for Indian context
- Both immediate relief and long-term strategies
- Markdown format with clear organization

Focus on evidence-based techniques that are practical for daily life.
            """,

            "meditation": f"""
Create a guided meditation script for someone experiencing {problem_category.value.replace('_', ' ')}.
{age_context}
Conversation context: {context_preview}

The meditation should:
- Be 5-15 minutes long
- Include specific instructions for posture, breathing, and focus
- Address the specific concerns mentioned
- Use calming, supportive language
- Be formatted in markdown with clear sections
- Include optional background on the meditation technique

Consider incorporating elements from Indian meditation traditions where appropriate.
            """,

            "study_techniques": f"""
Provide effective study techniques for academic stress and pressure.
{age_context}
Student's situation: {context_preview}

Include:
- Time management strategies
- Effective study methods
- Stress reduction while studying
- Organization techniques
- Exam preparation tips
- Indian education system considerations

Format in markdown with actionable sections and bullet points.
            """,

            "communication_techniques": f"""
Create a guide for improving communication in relationships.
{age_context}
Relationship context: {context_preview}

Cover:
- Active listening techniques
- Expressing feelings constructively  
- Conflict resolution strategies
- Setting healthy boundaries
- Cultural considerations for Indian relationships
- Family dynamics awareness

Use markdown formatting with practical examples and exercises.
            """
        }

        return resource_prompts.get(resource_type, f"""
Create a helpful resource about {resource_type} for someone dealing with {problem_category.value.replace('_', ' ')}.
{age_context}
Context: {context_preview}

Provide practical, actionable content that addresses the user's specific situation.
Use clear markdown formatting with headings, bullet points, and structured sections.
Make it culturally appropriate for Indian users.
        """)

    async def generate_wellness_insight(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized wellness insights based on user data patterns.

        Args:
            user_data: Dictionary containing user's mood entries, sessions, etc.

        Returns:
            Dictionary with wellness insights and recommendations
        """
        try:
            # Analyze patterns in user data
            mood_patterns = self._analyze_mood_patterns(user_data.get('mood_entries', []))
            chat_patterns = self._analyze_chat_patterns(user_data.get('chat_sessions', []))

            # Create insight prompt
            prompt = f"""
Based on the following user patterns, provide personalized wellness insights:

Mood Patterns: {json.dumps(mood_patterns, indent=2)}
Chat Patterns: {json.dumps(chat_patterns, indent=2)}

Generate insights that include:
1. Key patterns observed
2. Positive trends to acknowledge  
3. Areas for potential improvement
4. Specific, actionable recommendations
5. Encouraging perspective

Keep the tone supportive and non-judgmental. Focus on growth and self-compassion.
            """

            # Generate insights using text generation
            insights_text, _, _ = await self.generate_text_response(
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                "insights_text": insights_text,
                "mood_patterns": mood_patterns,
                "chat_patterns": chat_patterns,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating wellness insight: {e}")
            return {"error": "Failed to generate insights"}

    def _analyze_mood_patterns(self, mood_entries: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in mood entries."""
        if not mood_entries:
            return {"status": "no_data"}

        # Simple analysis - in production, this would be more sophisticated
        recent_moods = mood_entries[-7:]  # Last 7 entries
        mood_values = [entry.get('mood_value', 3) for entry in recent_moods]

        return {
            "recent_average": sum(mood_values) / len(mood_values) if mood_values else 3,
            "trend": "improving" if len(mood_values) > 1 and mood_values[-1] > mood_values[0] else "stable",
            "total_entries": len(mood_entries),
            "consistency": len(recent_moods) >= 5
        }

    def _analyze_chat_patterns(self, chat_sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in chat sessions."""
        if not chat_sessions:
            return {"status": "no_data"}

        # Analyze session frequency and topics
        recent_sessions = chat_sessions[-5:]  # Last 5 sessions
        problem_categories = [session.get('problem_category') for session in recent_sessions if session.get('problem_category')]

        return {
            "total_sessions": len(chat_sessions),
            "recent_sessions": len(recent_sessions),
            "common_topics": list(set(problem_categories)),
            "engagement_level": "high" if len(recent_sessions) >= 3 else "moderate"
        }

    async def get_latest_library_docs(self, library_name: str, topic: str = None) -> Optional[str]:
        """
        Get latest documentation for a library using MCP tools.
        This would integrate with the context7 MCP server for up-to-date docs.

        Args:
            library_name: Name of the library to get docs for
            topic: Specific topic within the library

        Returns:
            Latest documentation content or None if not found
        """
        try:
            # This would use MCP tools to get latest documentation
            # For now, return a placeholder
            logger.info(f"Fetching latest docs for {library_name} - topic: {topic}")

            # In actual implementation, this would call:
            # - mcp_context7_resolve-library-id to get the library ID
            # - mcp_context7_get-library-docs to get the documentation

            return f"Latest documentation for {library_name} would be fetched here using MCP tools."

        except Exception as e:
            logger.error(f"Error fetching library docs for {library_name}: {e}")
            return None
