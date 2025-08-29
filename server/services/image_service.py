"""
Image generation and editing service for Mitra AI.
Handles image creation and modification using Gemini.
"""

import asyncio
import logging
import io
from PIL import Image

from .base_gemini_service import BaseGeminiService
from core.config import settings

logger = logging.getLogger(__name__)


class ImageService(BaseGeminiService):
    """Service for image generation and editing."""

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