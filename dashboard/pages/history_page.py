"""
Session History Page
Shows all past processing sessions from the database.
"""

import streamlit as st
import pandas as pd
import sys
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
from database.db_handler import DatabaseHandler


def load_config() -> dict:
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def render_history():
    st.title("Session History")
    st.markdown("All past traffic monitoring sessions.")

    config = load_config()
    db = DatabaseHandler(config)
    sessions = db.get_all_sessions()
    db.close()

    if not sessions:
        st.warning("No sessions found. Run the pipeline first.")
        return

    df = pd.DataFrame(sessions)
    display_cols = [
        "session_id", "video_source", "status",
        "total_frames", "total_counted",
        "avg_density", "total_violations",
        "started_at", "ended_at"
    ]

    st.dataframe(
        df[display_cols].fillna("N/A"),
        use_container_width=True
    )

    st.markdown("---")
    st.metric("Total Sessions", len(sessions))
    completed = len([s for s in sessions if s["status"] == "completed"])
    st.metric("Completed", completed)