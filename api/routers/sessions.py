"""
Sessions Router
Returns session history from the database.
"""

import sys
import logging
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
from database.db_handler import DatabaseHandler

router = APIRouter()
logger = logging.getLogger(__name__)


def load_config() -> dict:
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


@router.get("/")
async def get_all_sessions():
    """Return all sessions."""
    db = DatabaseHandler(load_config())
    sessions = db.get_all_sessions()
    db.close()
    return sessions


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Return a specific session."""
    db = DatabaseHandler(load_config())
    session = db.get_session_summary(session_id)
    db.close()
    if not session:
        raise HTTPException(404, f"Session {session_id} not found.")
    return session


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session record."""
    db = DatabaseHandler(load_config())
    db.conn.execute(
        "DELETE FROM sessions WHERE session_id = ?", (session_id,)
    )
    db.conn.execute(
        "DELETE FROM frame_records WHERE session_id = ?", (session_id,)
    )
    db.conn.execute(
        "DELETE FROM vehicles WHERE session_id = ?", (session_id,)
    )
    db.conn.execute(
        "DELETE FROM violations WHERE session_id = ?", (session_id,)
    )
    db.conn.commit()
    db.close()
    return {"message": f"Session {session_id} deleted."}