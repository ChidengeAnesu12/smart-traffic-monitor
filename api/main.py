"""
FastAPI Backend
Serves the traffic monitoring CV pipeline as a REST API.
Supports video upload, live processing, and analytics queries.
"""

import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from api.routers import video, analytics, sessions, stream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

app = FastAPI(
    title="Smart Traffic Monitor API",
    description="Real-time traffic monitoring using YOLOv8 and DeepSORT",
    version="1.0.0",
)

# CORS — allow Next.js frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(video.router, prefix="/api/video", tags=["Video"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(stream.router, prefix="/api/stream", tags=["Stream"])


@app.get("/")
async def root():
    return {
        "name": "Smart Traffic Monitor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}