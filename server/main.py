"""
Main FastAPI application for Mitra AI server.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

from core.config import settings
from routers import chat, wellness, user


# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Mitra AI server...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Validate required environment variables
    if not settings.google_api_key:
        logger.error("GOOGLE_API_KEY environment variable is required")
        raise RuntimeError("Missing GOOGLE_API_KEY")
    
    if not settings.firebase_project_id:
        logger.error("FIREBASE_PROJECT_ID environment variable is required")
        raise RuntimeError("Missing FIREBASE_PROJECT_ID")
    
    logger.info("Server startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mitra AI server...")


# Create FastAPI application
app = FastAPI(
    title="Mitra AI",
    description="AI-powered mental wellness companion for Indian youth",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["mitra-ai.web.app", "mitra-ai.firebaseapp.com"]
    )

# Include routers
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(wellness.router, prefix="/api/v1/wellness", tags=["wellness"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Mitra AI - Your Mental Wellness Companion",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "timestamp": "2025-08-28T00:00:00Z"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail="Internal server error. Please try again later."
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )