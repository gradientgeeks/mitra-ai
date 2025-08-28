#!/usr/bin/env python3
"""
Development server runner for Mitra AI.
"""

import uvicorn
from core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=settings.debug
    )