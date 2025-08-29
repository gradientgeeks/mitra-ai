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
        
        # Base system instruction for Mitra AI
        self.base_system_instruction = """
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

    def _create_personalized_system_instruction(self, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create personalized system instruction based on user context."""
        if not user_context:
            return self.base_system_instruction
        
        personalization = []
        
        # Add personalized name
        mitra_name = user_context.get('mitra_name', 'Mitra')
        if mitra_name and mitra_name != 'Mitra':
            personalization.append(f"The user has chosen to call you '{mitra_name}' instead of Mitra. Use this name when referring to yourself.")
        
        # Add age-appropriate guidance
        age_group = user_context.get('age_group')
        if age_group:
            if age_group == "13-17":
                personalization.append("""
                Your user is a teenager (13-17). Tailor your responses accordingly:
                - Use relatable examples from school, friendships, and family situations
                - Be sensitive to academic pressure, peer relationships, and identity formation
                - Acknowledge the unique challenges of adolescence in Indian culture
                - Use slightly more casual but still respectful language
                - Be extra supportive about body image, social anxiety, and future concerns
                """)
            elif age_group == "18-24":
                personalization.append("""
                Your user is a young adult (18-24). Consider their life stage:
                - Address concerns about college, career choices, and independence
                - Be aware of the pressure of competitive exams and job market stress
                - Understand family expectations vs personal aspirations conflicts
                - Support with relationship concerns and social pressures
                - Acknowledge the transition from dependence to independence
                """)
            elif age_group == "25-34":
                personalization.append("""
                Your user is an adult (25-34). Focus on their concerns:
                - Career advancement, work-life balance, and professional stress
                - Relationship concerns, marriage expectations, and family planning
                - Financial responsibilities and independence
                - Balancing personal goals with family and social expectations
                - Support with major life decisions and transitions
                """)
            elif age_group == "35+":
                personalization.append("""
                Your user is a mature adult (35+). Consider their perspective:
                - Mid-life challenges, career transitions, and family responsibilities
                - Parenting concerns if applicable, caring for aging parents
                - Health and wellness focus, stress management
                - Reflection on life goals and achievements
                - Support with major life changes and finding meaning
                """)
        
        # Add gender-sensitive responses
        gender = user_context.get('gender')
        if gender and gender != 'prefer_not_to_say':
            if gender == 'female':
                personalization.append("""
                Be sensitive to challenges that women in India often face:
                - Societal expectations and pressures unique to women
                - Work-life balance and career vs family decisions
                - Safety concerns and social restrictions
                - Body image and self-worth issues in cultural context
                """)
            elif gender == 'male':
                personalization.append("""
                Be sensitive to challenges that men in India often face:
                - Pressure to be strong and not show vulnerability
                - Career and financial responsibility expectations
                - Emotional expression and seeking help stigma
                - Balancing traditional masculinity with emotional well-being
                """)
            elif gender == 'non_binary':
                personalization.append("""
                Be extra supportive and inclusive:
                - Acknowledge the unique challenges of gender identity in Indian society
                - Use inclusive language and avoid assumptions
                - Be sensitive to potential discrimination and acceptance issues
                - Focus on creating a safe, non-judgmental space
                """)
        
        # Add session-specific guidance based on current problem categories
        session_problem_categories = user_context.get('session_problem_categories', [])
        if session_problem_categories:
            category_guidance = {
                'anxiety': 'Be especially supportive about worry, fear, and anxious thoughts. Offer breathing exercises and grounding techniques.',
                'depression': 'Be gentle and understanding about low mood, hopelessness, and motivation issues. Encourage small steps and professional help.',
                'stress': 'Focus on stress management, time management, and healthy coping strategies. Address pressure from various sources.',
                'loneliness': 'Emphasize connection, community, and the importance of relationships. Be a warm, present companion.',
                'academic_pressure': 'Understand the intense competition and expectations in Indian education. Offer perspective and stress relief.',
                'relationship_issues': 'Be supportive about family, friendship, or romantic relationship challenges while respecting cultural values.',
                'self_esteem': 'Focus on building confidence, self-worth, and positive self-image. Challenge negative self-talk gently.',
                'career_confusion': 'Help with decision-making, exploring options, and managing uncertainty about the future.',
                'family_problems': 'Be sensitive to complex family dynamics in Indian culture, respect for elders, and generational differences.',
                'general_wellbeing': 'Take a holistic approach to mental health, lifestyle, and overall life satisfaction.'
            }
            
            problem_focus = []
            for category in session_problem_categories:
                if category in category_guidance:
                    problem_focus.append(f"- {category_guidance[category]}")
            
            if problem_focus:
                personalization.append("Current session focus areas:\n" + "\n".join(problem_focus))
        
        # Combine base instruction with personalizations
        if personalization:
            return self.base_system_instruction + "\n\nPersonalization for this user:\n" + "\n".join(personalization)
        
        return self.base_system_instruction

    async def generate_text_response(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
        include_grounding: bool = False,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Optional[List[GroundingSource]], Optional[str]]:
        """
        Generate text response using Gemini.
        
        Args:
            messages: Conversation history
            config: Generation configuration
            include_grounding: Whether to use Google Search grounding
            user_context: User context for personalization
            
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
            
            # Create personalized system instruction
            system_instruction = self._create_personalized_system_instruction(user_context)
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.gemini_text_model,
                contents=gemini_messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
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
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bytes, Optional[str]]:
        """
        Generate voice response using Gemini Live API.
        
        Args:
            messages: Conversation history
            voice: Voice to use for generation
            language: Language code
            user_context: User context for personalization
            
        Returns:
            Tuple of (audio_data, transcription)
        """
        try:
            # Convert messages to text format for Live API
            conversation_text = ""
            for msg in messages:
                role = "User" if msg.role == MessageRole.USER else "Assistant"
                if msg.content.text:
                    conversation_text += f"{role}: {msg.content.text}\n"
            
            # Create personalized system instruction
            system_instruction = self._create_personalized_system_instruction(user_context)
            
            # Use Live API for voice generation
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {"prebuilt_voice_config": {"voice_name": voice}}
                },
                "system_instruction": system_instruction
            }
            
            async with self.client.aio.live.connect(
                model=settings.gemini_live_model,
                config=config
            ) as session:
                # Send the latest user message for response
                if messages:
                    latest_message = messages[-1]
                    if latest_message.role == MessageRole.USER and latest_message.content.text:
                        await session.send(latest_message.content.text)
                        
                        # Receive audio response
                        audio_chunks = []
                        transcription = ""
                        
                        async for response in session.receive():
                            if hasattr(response, 'audio') and response.audio:
                                audio_chunks.append(response.audio)
                            if hasattr(response, 'text') and response.text:
                                transcription += response.text
                                
                        # Combine audio chunks
                        audio_data = b''.join(audio_chunks) if audio_chunks else b''
                        return audio_data, transcription
                        
            return b'', None
            
        except Exception as e:
            logger.error(f"Error generating voice response: {e}")
            # Fallback to text generation and synthetic audio
            text_response, _, _ = await self.generate_text_response(messages, user_context=user_context)
            return b'', text_response  # Return empty audio with text fallback

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

    async def analyze_conversation_for_problems(
        self,
        messages: List[ChatMessage]
    ) -> List[str]:
        """Analyze conversation to identify problem categories."""
        try:
            # Extract text content from messages
            conversation_text = ""
            for msg in messages[-10:]:  # Analyze last 10 messages
                if msg.content.text and msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                    role = "User" if msg.role == MessageRole.USER else "Mitra"
                    conversation_text += f"{role}: {msg.content.text}\n"
            
            if not conversation_text:
                return []
            
            analysis_prompt = f"""
            Analyze this conversation and identify which mental health problem categories are being discussed.
            Only return categories that are clearly evident from the conversation content.
            
            Conversation:
            {conversation_text}
            
            Available categories:
            - anxiety: Worry, fear, nervousness, panic
            - depression: Sadness, hopelessness, low mood
            - stress: Feeling overwhelmed, pressure, tension
            - loneliness: Social isolation, feeling alone
            - academic_pressure: Study stress, exam anxiety, performance pressure
            - relationship_issues: Family, friends, romantic relationships
            - self_esteem: Self-worth, confidence, body image
            - career_confusion: Job uncertainty, future planning
            - family_problems: Family conflicts, generational issues
            - general_wellbeing: Overall life satisfaction, health
            
            Return only the category names that apply, as a JSON array of strings.
            """
            
            response = await self.generate_structured_content(
                analysis_prompt,
                {
                    "type": "array",
                    "items": {"type": "string"}
                }
            )
            
            # Validate categories
            valid_categories = [
                "anxiety", "depression", "stress", "loneliness", "academic_pressure",
                "relationship_issues", "self_esteem", "career_confusion", 
                "family_problems", "general_wellbeing"
            ]
            
            if isinstance(response, list):
                return [cat for cat in response if cat in valid_categories]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error analyzing conversation for problems: {e}")
            return []

    async def generate_session_resources(
        self,
        problem_categories: List[str],
        conversation_summary: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate helpful resources based on session problem categories."""
        try:
            age_group = user_context.get('age_group', 'young_adult') if user_context else 'young_adult'
            gender = user_context.get('gender', 'prefer_not_to_say') if user_context else 'prefer_not_to_say'
            
            resource_prompt = f"""
            Generate helpful mental health resources for someone with these characteristics:
            - Age group: {age_group}
            - Gender: {gender}
            - Problem areas: {', '.join(problem_categories)}
            - Session summary: {conversation_summary}
            
            Generate 3-5 practical resources. Each resource should be culturally appropriate for young people in India.
            
            Return as JSON array with this format:
            [
                {{
                    "type": "breathing_technique|meditation|exercise|article|coping_strategy|professional_help",
                    "title": "Resource title",
                    "description": "Brief description",
                    "content": "Detailed instructions or content",
                    "duration": "5-10 minutes",
                    "difficulty": "easy|medium|hard",
                    "category": "problem category this addresses"
                }}
            ]
            """
            
            response = await self.generate_structured_content(
                resource_prompt,
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "content": {"type": "string"},
                            "duration": {"type": "string"},
                            "difficulty": {"type": "string"},
                            "category": {"type": "string"}
                        }
                    }
                }
            )
            
            return response if isinstance(response, list) else []
            
        except Exception as e:
            logger.error(f"Error generating session resources: {e}")
            return []