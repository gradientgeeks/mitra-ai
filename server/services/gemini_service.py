"""
Gemini AI service for all AI interactions in Mitra AI.
Handles text generation, voice conversations, image generation, and grounding.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator, Tuple
from datetime import datetime
import base64
import io
from google import genai
from google.genai import types
from PIL import Image

from core.config import settings
from models.chat import ChatMessage, MessageRole, MessageType, SafetyStatus
from models.common import GroundingSource, GenerationConfig

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for all Gemini AI interactions."""
    
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

    async def generate_text_response(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
        include_grounding: bool = False
    ) -> Tuple[str, Optional[List[GroundingSource]], Optional[str]]:
        """
        Generate text response using Gemini.
        
        Args:
            messages: Conversation history
            config: Generation configuration
            include_grounding: Whether to use Google Search grounding
            
        Returns:
            Tuple of (response_text, grounding_sources, thinking_text)
        """
        try:
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Prepare tools
            tools = []
            if include_grounding:
                tools.append(types.Tool(google_search=types.GoogleSearch()))
            
            # Prepare generation config
            gen_config = self._prepare_generation_config(config)
            
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

    async def generate_voice_response(
        self,
        messages: List[ChatMessage],
        voice: str = "Puck",
        language: str = "en"
    ) -> Tuple[bytes, Optional[str]]:
        """
        Generate voice response using Gemini Live API.
        
        Args:
            messages: Conversation history
            voice: Voice to use for generation
            language: Language code
            
        Returns:
            Tuple of (audio_data, transcription)
        """
        try:
            # Convert messages to text format for Live API
            conversation_text = self._convert_messages_to_text(messages)
            
            # Configure Live API session
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {"name": voice},
                    "language_config": {"language_code": language}
                },
                "output_audio_transcription": {}
            }
            
            # Connect to Live API and generate response
            async with self.client.aio.live.connect(
                model=settings.gemini_live_model,
                config=config
            ) as session:
                # Send conversation history as context
                await session.send_client_content(
                    turns=[{"role": "user", "parts": [{"text": conversation_text}]}],
                    turn_complete=True
                )
                
                # Collect audio response
                audio_chunks = []
                transcription = None
                
                async for message in session.receive():
                    if hasattr(message, 'server_content'):
                        for part in message.server_content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                audio_chunks.append(part.inline_data.data)
                            elif hasattr(part, 'text') and part.text:
                                transcription = part.text
                
                # Combine audio chunks
                audio_data = b''.join(audio_chunks) if audio_chunks else b''
                return audio_data, transcription
                
        except Exception as e:
            logger.error(f"Error generating voice response: {e}")
            raise

    async def process_voice_input(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> str:
        """
        Process voice input and convert to text.
        
        Args:
            audio_data: PCM audio data
            sample_rate: Audio sample rate
            
        Returns:
            Transcribed text
        """
        try:
            # Configure Live API for audio-to-text
            config = {
                "response_modalities": ["TEXT"],
                "input_audio_transcription": {}
            }
            
            async with self.client.aio.live.connect(
                model=settings.gemini_live_model,
                config=config
            ) as session:
                # Send audio data
                mime_type = f"audio/pcm;rate={sample_rate}"
                audio_blob = types.Blob(
                    mime_type=mime_type,
                    data=audio_data
                )
                
                await session.send_client_content(
                    turns=[{"role": "user", "parts": [audio_blob]}],
                    turn_complete=True
                )
                
                # Receive transcription
                transcription = ""
                async for message in session.receive():
                    if hasattr(message, 'server_content'):
                        for part in message.server_content.parts:
                            if hasattr(part, 'text') and part.text:
                                transcription += part.text
                
                return transcription.strip()
                
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            raise

    async def generate_image(
        self,
        prompt: str,
        style: str = "realistic"
    ) -> bytes:
        """
        Generate image using Gemini.
        
        Args:
            prompt: Image generation prompt
            style: Image style preference
            
        Returns:
            Generated image data
        """
        try:
            # Enhance prompt for mental wellness context
            enhanced_prompt = f"""
            Create a calming, supportive image for mental wellness: {prompt}
            
            Style: {style}, soothing colors, peaceful atmosphere, 
            culturally appropriate for young Indian audience.
            Avoid any disturbing or triggering content.
            """
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.gemini_image_model,
                contents=[enhanced_prompt]
            )
            
            # Extract image data
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return part.inline_data.data
            
            raise ValueError("No image generated in response")
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise

    async def edit_image(
        self,
        image_data: bytes,
        edit_prompt: str
    ) -> bytes:
        """
        Edit an existing image using text prompts.
        
        Args:
            image_data: Original image data
            edit_prompt: Editing instructions
            
        Returns:
            Edited image data
        """
        try:
            # Convert image data to PIL Image for processing
            image = Image.open(io.BytesIO(image_data))
            
            # Create edit prompt
            prompt = f"""
            Edit this image based on the following instructions: {edit_prompt}
            
            Maintain the peaceful, supportive nature appropriate for mental wellness.
            Keep the style consistent and avoid any disturbing elements.
            """
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.gemini_image_model,
                contents=[prompt, image]
            )
            
            # Extract edited image data
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return part.inline_data.data
            
            raise ValueError("No edited image generated in response")
            
        except Exception as e:
            logger.error(f"Error editing image: {e}")
            raise

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
                import json
                return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Error generating structured content: {e}")
            raise

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
            
            return await self.generate_structured_content(prompt, schema)
            
        except Exception as e:
            logger.error(f"Error generating wellness insight: {e}")
            raise

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