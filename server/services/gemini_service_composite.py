"""
Composite Gemini service that provides access to all separate services.
This maintains backward compatibility while using the new modular services.
"""

from .base_gemini_service import BaseGeminiService
from .text_generation_service import TextGenerationService
from .voice_service import VoiceService
from .image_service import ImageService
from .wellness_service import WellnessService


class GeminiService(BaseGeminiService):
    """
    Composite service that provides access to all Gemini AI capabilities.
    Delegates to specialized services while maintaining the original interface.
    """
    
    def __init__(self):
        """Initialize all specialized services."""
        super().__init__()
        self.text_service = TextGenerationService()
        self.voice_service = VoiceService()
        self.image_service = ImageService()
        self.wellness_service = WellnessService()
    
    # Text generation methods - delegate to TextGenerationService
    async def generate_text_response(self, messages, config=None, include_grounding=False):
        """Generate text response using Gemini (legacy method)."""
        return await self.text_service.generate_text_response_legacy(
            messages, config, include_grounding
        )
    
    async def generate_personalized_text_response(self, messages, user_profile=None, problem_category=None, config=None, include_grounding=False):
        """Generate personalized text response using Gemini."""
        return await self.text_service.generate_text_response(
            messages, user_profile, problem_category, config, include_grounding
        )
    
    async def generate_structured_content(self, prompt, schema):
        """Generate structured content using response schema."""
        return await self.text_service.generate_structured_content(prompt, schema)
    
    # Voice methods - delegate to VoiceService
    async def generate_voice_response(self, messages, user_profile=None, problem_category=None, voice=None, language="en"):
        """Generate personalized voice response using Gemini Live API."""
        return await self.voice_service.generate_voice_response(messages, user_profile, problem_category, voice, language)
    
    async def process_voice_input(self, audio_data, sample_rate=16000):
        """Process voice input and convert to text."""
        return await self.voice_service.process_voice_input(audio_data, sample_rate)
    
    # Image methods - delegate to ImageService
    async def generate_image(self, prompt, style="realistic"):
        """Generate image using Gemini."""
        return await self.image_service.generate_image(prompt, style)
    
    async def edit_image(self, image_data, edit_prompt):
        """Edit an existing image using text prompts."""
        return await self.image_service.edit_image(image_data, edit_prompt)
    
    # Wellness methods - delegate to WellnessService
    async def generate_meditation_script(self, meditation_type, duration_minutes, focus_area=None):
        """Generate a custom meditation script."""
        return await self.wellness_service.generate_meditation_script(
            meditation_type, duration_minutes, focus_area
        )
    
    async def generate_wellness_insight(self, user_data):
        """Generate personalized wellness insights based on user data."""
        return await self.wellness_service.generate_wellness_insight(user_data)
    
    async def generate_coping_strategy(self, emotion, situation, user_preferences=None):
        """Generate personalized coping strategies."""
        return await self.wellness_service.generate_coping_strategy(
            emotion, situation, user_preferences
        )
    
    async def generate_mood_check_in(self, previous_mood_data=None):
        """Generate personalized mood check-in questions and prompts."""
        return await self.wellness_service.generate_mood_check_in(previous_mood_data)