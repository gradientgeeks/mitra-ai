"""
Text generation service for Mitra AI.
Handles text responses, structured content, and grounding.
"""

import asyncio
import logging
import json
from typing import Optional, List, Dict, Any, Tuple

from google.genai import types

from .base_gemini_service import BaseGeminiService
from core.config import settings
from models.chat import ChatMessage
from models.common import GenerationConfig, GroundingSource
from models.user import UserProfile, ProblemCategory

logger = logging.getLogger(__name__)


class TextGenerationService(BaseGeminiService):
    """Service for text generation and structured content."""

    async def generate_text_response(
        self,
        messages: List[ChatMessage],
        user_profile: Optional[UserProfile] = None,
        problem_category: Optional[ProblemCategory] = None,
        config: Optional[GenerationConfig] = None,
        include_grounding: bool = False
    ) -> Tuple[str, Optional[List[GroundingSource]], Optional[str]]:
        """
        Generate personalized text response using Gemini.
        
        Args:
            messages: Conversation history
            user_profile: User profile for personalization
            problem_category: Current session problem category
            config: Generation configuration
            include_grounding: Whether to use Google Search grounding
            
        Returns:
            Tuple of (response_text, grounding_sources, thinking_text)
        """
        try:
            # Get personalized system instruction
            system_instruction = self.get_personalized_system_instruction(user_profile, problem_category)
            
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Prepare tools
            tools = []
            if include_grounding:
                tools.append(types.Tool(google_search=types.GoogleSearch()))
            
            # Prepare generation config
            gen_config = self._prepare_generation_config(config)
            
            # Add system instruction to config
            gen_config["system_instruction"] = system_instruction
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.gemini_text_model,
                contents=gemini_messages,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=tools if tools else None,
                    **gen_config
                )
            )
            
            # Extract response components
            response_text = response.text if response.text else ""
            thinking_text = None
            grounding_sources = None
            
            # Extract thinking if available (Gemini 2.5)
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'thinking') and candidate.thinking:
                    thinking_text = candidate.thinking
                
                # Extract grounding metadata if available
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_sources = self._extract_grounding_sources(candidate.grounding_metadata)
            
            return response_text, grounding_sources, thinking_text
            
        except Exception as e:
            logger.error(f"Error generating text response: {e}")
            raise

    # Backward compatibility method
    async def generate_text_response_legacy(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
        include_grounding: bool = False
    ) -> Tuple[str, Optional[List[GroundingSource]], Optional[str]]:
        """Legacy method for backward compatibility."""
        return await self.generate_text_response(
            messages=messages,
            user_profile=None,
            problem_category=None,
            config=config,
            include_grounding=include_grounding
        )

    async def generate_structured_content(
        self,
        prompt: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate structured content using response schema.
        
        Args:
            prompt: Generation prompt
            schema: JSON schema for structured output
            
        Returns:
            Structured content matching schema
        """
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.gemini_text_model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_schema=schema
                )
            )
            
            # Parse structured response
            if hasattr(response, 'parsed') and response.parsed:
                return response.parsed
            else:
                # Fallback to parsing text response as JSON
                return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Error generating structured content: {e}")
            raise