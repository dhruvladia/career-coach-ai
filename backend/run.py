#!/usr/bin/env python3
"""
Simple script to run the LearnTube AI Career Coach backend
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 