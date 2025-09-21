"""
Gemini AI service for all AI interactions in Mitra AI.
This is now a composite service that delegates to specialized services.
Maintains backward compatibility with the original interface.
"""

# Import the composite service implementation
from .gemini_service_composite import GeminiService

# Re-export the main service class
__all__ = ['GeminiService']
