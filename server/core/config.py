"""
Core configuration for Mitra AI server.
Handles environment variables and application settings.
"""

import os
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv() 


class Settings(BaseModel):
    """Application settings configuration."""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "development"
    
    # Google Cloud Configuration
    google_api_key: Optional[str] = None
    google_cloud_project: Optional[str] = None
    
    # Firebase Configuration
    firebase_credentials_path: Optional[str] = None
    firebase_project_id: Optional[str] = None
    
    # Security
    allowed_origins: list[str] = [
        "*",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://mitra-ai.web.app",
        "https://mitra-ai.firebaseapp.com"
    ]
    
    # Gemini Models
    gemini_text_model: str = "gemini-2.5-flash"
    gemini_live_model: str = "gemini-live-2.5-flash-preview"
    gemini_image_model: str = "gemini-2.5-flash-image-preview"
    
    # Crisis Detection Keywords (in multiple Indian languages)
    crisis_keywords: list[str] = [
        # English
        "suicide", "kill myself", "end my life", "hurt myself", "self harm",
        "want to die", "no point living", "end it all", "cut myself",
        
        # Hindi
        "आत्महत्या", "खुद को मारना", "जान देना", "मरना चाहता", "खुद को नुकसान",
        
        # Common phrases
        "can't take it anymore", "nobody cares", "better off dead",
        "नहीं रह सकता", "कोई परवाह नहीं", "मरना बेहतर"
    ]
    
    # Indian Crisis Helplines
    crisis_helplines: dict = {
        "AASRA": {
            "number": "91-22-27546669",
            "website": "http://www.aasra.info/",
            "description": "24x7 emotional support"
        },
        "Vandrevala Foundation": {
            "number": "9999666555",
            "website": "https://www.vandrevalafoundation.com/",
            "description": "24x7 free helpline"
        },
        "Sneha": {
            "number": "91-44-24640050",
            "website": "http://www.snehaindia.org/",
            "description": "Chennai-based crisis helpline"
        },
        "iCall": {
            "number": "9152987821",
            "website": "https://icallhelpline.org/",
            "description": "Psychosocial helpline"
        }
    }
    
    # Safety thresholds
    crisis_confidence_threshold: float = 0.7
    safety_check_enabled: bool = True
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load from environment variables
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        self.firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Port from environment
        port_env = os.getenv("PORT")
        if port_env:
            self.port = int(port_env)


# Global settings instance
settings = Settings()