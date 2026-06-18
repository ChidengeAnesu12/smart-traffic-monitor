"""
Analytics Page
Shows charts and metrics from the most recent session.
"""

import streamlit as st
import sys
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from components.charts import (
    render_density_chart,
    render_vehicle_type_chart,
    render_speed_chart,
    render_zone_chart,
)
from components.metrics import (
    render_metric_row,
    render_density_badge,
)


def load_config() -> dict:
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def render_analytics():
    st.title("Traffic Analytics")

    config = load_config()
    db = DatabaseHandler(config)
    sessions = db.get_all_sessions()

    if not sessions:
        st.warning("No sessions found. Run the pipeline first.")
        db.close()
        return

    # Session selector
    session_ids = [s["session_id"] for s in sessions]
    selected = st.selectbox("Select Session", session_ids)

    session = db.get_session_summary(selected)
    frame_records = db.get_frame_records(selected)
    vehicle_records = db.get_vehicles(selected)
    db.close()

    if not session:
        st.error("Session not found.")
        return

    # Top metrics
    st.markdown("---")
    render_metric_row({
        "Total Frames":    session["total_frames"],
        "Vehicles Counted": session["total_counted"],
        "Avg Density":     f"{session['avg_density']:.1%}",
        "Peak Density":    f"{session['peak_density']:.1%}",
        "Violations":      session["total_violations"],
        "Status":          session["status"].upper(),
    })

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        render_density_chart(frame_records)
    with col2:
        render_vehicle_type_chart(vehicle_records)

    col3, col4 = st.columns(2)
    with col3:
        render_speed_chart(vehicle_records)
    with col4:
        render_zone_chart(vehicle_records)

    # Vehicle table
    st.markdown("---")
    st.subheader("Vehicle Records")
    if vehicle_records:
        import pandas as pd
        df = pd.DataFrame(vehicle_records)
        display_cols = [
            "track_id", "label", "avg_speed_kmh",
            "max_speed_kmh", "zone", "violation"
        ]
        st.dataframe(
            df[display_cols].fillna("N/A"),
            use_container_width=True
        )

    # Heatmap
    st.markdown("---")
    st.subheader("Traffic Heatmap")
    heatmap_path = "data/outputs/heatmap.jpg"
    if Path(heatmap_path).exists():
        st.image(heatmap_path, use_container_width=True)
    else:
        st.info("No heatmap available. Run the pipeline first.")