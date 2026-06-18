"""
Chart components for analytics dashboard.
"""

import streamlit as st
import pandas as pd


def render_density_chart(frame_records: list) -> None:
    """Render vehicle count over time chart."""
    if not frame_records:
        st.info("No frame data available.")
        return

    df = pd.DataFrame(frame_records)
    df = df[["frame_number", "vehicle_count", "density_score"]]

    st.subheader("Vehicle Count Over Time")
    st.line_chart(df.set_index("frame_number")["vehicle_count"])

    st.subheader("Density Score Over Time")
    st.area_chart(df.set_index("frame_number")["density_score"])


def render_vehicle_type_chart(vehicle_records: list) -> None:
    """Render vehicle type distribution bar chart."""
    if not vehicle_records:
        st.info("No vehicle data available.")
        return

    df = pd.DataFrame(vehicle_records)
    type_counts = df["label"].value_counts().reset_index()
    type_counts.columns = ["Vehicle Type", "Count"]

    st.subheader("Vehicle Type Distribution")
    st.bar_chart(type_counts.set_index("Vehicle Type"))


def render_speed_chart(vehicle_records: list) -> None:
    """Render speed distribution chart."""
    if not vehicle_records:
        return

    df = pd.DataFrame(vehicle_records)
    speed_df = df[df["avg_speed_kmh"].notna()][
        ["track_id", "avg_speed_kmh", "label"]
    ]

    if speed_df.empty:
        st.info("No speed data available.")
        return

    st.subheader("Speed per Vehicle (km/h)")
    st.bar_chart(
        speed_df.set_index("track_id")["avg_speed_kmh"]
    )


def render_zone_chart(vehicle_records: list) -> None:
    """Render zone distribution chart."""
    if not vehicle_records:
        return

    df = pd.DataFrame(vehicle_records)
    zone_counts = df["zone"].value_counts().reset_index()
    zone_counts.columns = ["Zone", "Count"]

    st.subheader("Vehicle Zone Distribution")
    st.bar_chart(zone_counts.set_index("Zone"))