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

logger = logging.getLogger(__name__)


class BaseGeminiService:
    """Base service for common Gemini AI functionality."""
    
    def __init__(self):
        """Initialize Gemini client."""
        self.client = genai.Client(api_key=settings.google_api_key)
        
        # System instruction for Mitra AI
        self.system_instruction = """
        You are Mitra (मित्र), a compassionate and empathetic AI companion designed to support 
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