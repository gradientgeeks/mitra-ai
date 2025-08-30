"""
Enhanced wellness service with MCP integration for generating contextual resources.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.user import ProblemCategory, UserProfile
from models.wellness import GeneratedResource, ResourceType
from services.mcp_integration_service import MCPIntegrationService
from services.resource_generation_service import ResourceGenerationService

logger = logging.getLogger(__name__)


class EnhancedWellnessService:
    """Enhanced wellness service with MCP integration capabilities."""

    def __init__(self):
        """Initialize enhanced wellness service."""
        self.mcp_service = MCPIntegrationService()
        self.resource_service = ResourceGenerationService()

    async def generate_session_resources(
        self,
        problem_category: ProblemCategory,
        user_profile: Optional[UserProfile],
        session_context: str,
        resource_types: Optional[List[str]] = None,
        max_resources: int = 3
    ) -> List[GeneratedResource]:
        """
        Generate enhanced resources using both wellness expertise and MCP tools.

        Args:
            problem_category: The main problem category being discussed
            user_profile: User profile for personalization
            session_context: Context from recent messages in the session
            resource_types: Specific resource types to generate
            max_resources: Maximum number of resources to generate

        Returns:
            List of generated resources with latest documentation and contextual guidance
        """
        try:
            # Generate tech-aware resources using MCP integration
            mcp_resources = await self.mcp_service.generate_tech_resources_for_chat(
                session_context=session_context,
                user_profile=user_profile,
                problem_category=problem_category
            )

            # Generate traditional wellness resources
            wellness_resources = await self.resource_service.generate_session_resources(
                problem_category=problem_category,
                user_profile=user_profile,
                session_context=session_context,
                resource_types=resource_types,
                max_resources=max_resources - len(mcp_resources)
            )

            # Combine and prioritize resources
            all_resources = mcp_resources + wellness_resources

            # Limit to max_resources
            return all_resources[:max_resources]

        except Exception as e:
            logger.error(f"Error generating enhanced session resources: {e}")
            # Fallback to basic resource generation
            return await self.resource_service.generate_session_resources(
                problem_category=problem_category,
                user_profile=user_profile,
                session_context=session_context,
                resource_types=resource_types,
                max_resources=max_resources
            )

    async def generate_real_time_support(
        self,
        current_message: str,
        problem_category: ProblemCategory,
        user_profile: Optional[UserProfile]
    ) -> Optional[GeneratedResource]:
        """
        Generate immediate support resource based on current message analysis.

        Args:
            current_message: The user's current message
            problem_category: Problem category for the session
            user_profile: User profile for personalization

        Returns:
            Immediate support resource or None
        """
        try:
            # Analyze current message for urgency and content
            urgency_level = self._assess_message_urgency(current_message)

            if urgency_level == "high":
                # Generate immediate coping strategy
                return await self.resource_service._generate_specific_resource(
                    resource_type="immediate_coping",
                    problem_category=problem_category,
                    user_profile=user_profile,
                    session_context=current_message
                )
            elif urgency_level == "medium":
                # Generate supportive guidance
                return await self.resource_service._generate_specific_resource(
                    resource_type="supportive_guidance",
                    problem_category=problem_category,
                    user_profile=user_profile,
                    session_context=current_message
                )

            return None

        except Exception as e:
            logger.error(f"Error generating real-time support: {e}")
            return None

    def _assess_message_urgency(self, message: str) -> str:
        """Assess the urgency level of a user message."""
        message_lower = message.lower()

        # High urgency indicators
        high_urgency_words = [
            'crisis', 'emergency', 'urgent', 'can\'t cope', 'breaking down',
            'overwhelming', 'can\'t handle', 'desperate', 'help me now'
        ]

        # Medium urgency indicators
        medium_urgency_words = [
            'stressed', 'anxious', 'worried', 'confused', 'stuck',
            'don\'t know what to do', 'need help', 'feeling bad'
        ]

        if any(word in message_lower for word in high_urgency_words):
            return "high"
        elif any(word in message_lower for word in medium_urgency_words):
            return "medium"
        else:
            return "low"
