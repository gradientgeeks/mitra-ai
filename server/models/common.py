"""
Common response models and base classes.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum


class APIStatus(str, Enum):
    """API response status."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ErrorType(str, Enum):
    """Types of errors."""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    CRISIS_DETECTED = "crisis_detected"


class APIResponse(BaseModel):
    """Base API response model."""
    status: APIStatus
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    status: APIStatus = APIStatus.ERROR
    error_type: ErrorType
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    data: List[Any]
    pagination: Dict[str, Any]
    total_count: int
    has_next: bool
    has_previous: bool


class HealthCheck(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    services: Dict[str, str] = {
        "database": "healthy",
        "gemini_api": "healthy",
        "firebase": "healthy"
    }


class GroundingSource(BaseModel):
    """Grounding source information."""
    title: str
    url: str
    snippet: str
    relevance_score: Optional[float] = None


class GenerationConfig(BaseModel):
    """Configuration for AI generation."""
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=1, le=100)
    thinking_budget: Optional[int] = Field(None, ge=0, le=10000)
    enable_grounding: bool = False
    enable_safety_check: bool = True