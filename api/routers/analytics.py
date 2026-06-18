"""
Analytics Router
Returns analytics data from the database.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import yaml
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
from database.db_handler import DatabaseHandler

router = APIRouter()
logger = logging.getLogger(__name__)


def load_config() -> dict:
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def get_db() -> DatabaseHandler:
    return DatabaseHandler(load_config())


@router.get("/summary/{session_id}")
async def get_summary(session_id: str):
    """Get analytics summary for a session."""
    db = get_db()
    summary = db.get_session_summary(session_id)
    db.close()
    if not summary:
        raise HTTPException(404, f"Session {session_id} not found.")
    return summary


@router.get("/frames/{session_id}")
async def get_frames(session_id: str, limit: int = 200):
    """Get frame records for density chart."""
    db = get_db()
    records = db.get_frame_records(session_id)
    db.close()
    return records[-limit:]


@router.get("/vehicles/{session_id}")
async def get_vehicles(session_id: str):
    """Get vehicle records for a session."""
    db = get_db()
    vehicles = db.get_vehicles(session_id)
    db.close()
    return vehicles


@router.get("/violations/{session_id}")
async def get_violations(session_id: str):
    """Get violation records for a session."""
    db = get_db()
    violations = db.get_violations(session_id)
    db.close()
    return violations


@router.get("/heatmap/{job_id}")
async def get_heatmap(job_id: str):
    """Return heatmap image for a job."""
    path = f"data/outputs/{job_id}_heatmap.jpg"
    if not Path(path).exists():
        raise HTTPException(404, "Heatmap not found.")
    return FileResponse(path, media_type="image/jpeg")