"""
Live Processing Page
Upload a video and run the full pipeline.
"""

import streamlit as st
import sys
import tempfile
import cv2
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from detection.detector import VehicleDetector
from detection.utils import (
    draw_tracks, draw_stats, draw_counting_line,
    draw_density, draw_speed, draw_zones,
    draw_violations, resize_frame
)
from tracking.tracker import VehicleTracker
from counting.counter import VehicleCounter
from analytics.density import TrafficDensityAnalyzer
from analytics.speed import SpeedEstimator
from analytics.lane_violation import LaneViolationDetector
from analytics.heatmap import TrafficHeatmap
from analytics.analytics_engine import AnalyticsEngine
from database.db_handler import DatabaseHandler


def load_config() -> dict:
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def render_live_processing():
    st.title("Live Traffic Processing")
    st.markdown("Upload a traffic video to run the full detection pipeline.")

    config = load_config()

    uploaded_file = st.file_uploader(
        "Upload Traffic Video",
        type=["mp4", "avi", "mov"],
    )

    col1, col2 = st.columns(2)
    with col1:
        confidence = st.slider(
            "Detection Confidence", 0.1, 0.9,
            float(config["model"]["confidence"]), 0.05
        )
    with col2:
        line_pos = st.slider(
            "Counting Line Position", 0.1, 0.9,
            float(config["counting"]["line_position"]), 0.05
        )

    config["model"]["confidence"] = confidence
    config["counting"]["line_position"] = line_pos

    if uploaded_file is None:
        st.info("Please upload a video file to begin.")
        return

    run_btn = st.button("Run Pipeline", type="primary")
    if not run_btn:
        return

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".mp4"
    ) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    config["video"]["source"] = tmp_path

    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    # Initialize modules
    detector = VehicleDetector(config)
    tracker = VehicleTracker(config)
    counter = VehicleCounter(config, frame_height)
    density_analyzer = TrafficDensityAnalyzer(config)
    speed_estimator = SpeedEstimator(config, 30.0)
    lane_detector = LaneViolationDetector(config, frame_width)
    heatmap = TrafficHeatmap(frame_width, frame_height)
    analytics = AnalyticsEngine(config)
    db = DatabaseHandler(config)
    db.create_session(analytics.session_id, uploaded_file.name)

    cap = cv2.VideoCapture(tmp_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    speed_estimator.fps = fps

    # UI placeholders
    st.markdown("---")
    progress = st.progress(0)
    status = st.empty()

    col_a, col_b, col_c, col_d = st.columns(4)
    metric_vehicles = col_a.empty()
    metric_counted = col_b.empty()
    metric_density = col_c.empty()
    metric_violations = col_d.empty()

    frame_display = st.empty()

    frame_count = 0
    last_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame, frame_width, frame_height)
        last_frame = frame.copy()

        detections = detector.detect(frame)
        tracked_objects = tracker.update(detections, frame)
        tracked_with_speed = speed_estimator.update(tracked_objects)
        tracked_with_violations = lane_detector.update(
            tracked_with_speed, frame_count
        )
        counts = counter.update(tracked_objects)
        density_report = density_analyzer.update(tracked_objects)
        heatmap.update(tracked_objects)
        analytics.record_frame(
            frame_count, tracked_with_violations,
            density_report, counts
        )

        annotated = draw_zones(frame, lane_detector.zones)
        annotated = draw_tracks(annotated, tracked_with_violations)
        annotated = draw_speed(annotated, tracked_with_violations)
        annotated = draw_violations(annotated, tracked_with_violations)
        annotated = draw_counting_line(
            annotated, counter.line_y, counts["total"]
        )
        annotated = draw_density(annotated, density_report)
        annotated = draw_stats(annotated, {
            "Vehicles": density_report["vehicle_count"],
            "Level": density_report["level"],
            "Counted": counts["total"],
        })

        # Update UI every 5 frames
        if frame_count % 5 == 0:
            rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            frame_display.image(rgb, use_container_width=True)
            metric_vehicles.metric(
                "Vehicles", density_report["vehicle_count"]
            )
            metric_counted.metric("Counted", counts["total"])
            metric_density.metric(
                "Density", f"{density_report['density_score']:.0%}"
            )
            metric_violations.metric(
                "Violations", len(lane_detector.violations)
            )
            progress.progress(frame_count / total_frames)
            status.text(f"Processing frame {frame_count}/{total_frames}")

        frame_count += 1

    cap.release()
    progress.progress(1.0)
    status.text("Processing complete!")

    # Save to DB
    summary = analytics.get_summary()
    db.update_session(analytics.session_id, summary)
    db.insert_frame_records(
        analytics.session_id, analytics.frame_records
    )
    db.insert_vehicles(
        analytics.session_id, analytics.vehicle_records
    )
    db.insert_violations(
        analytics.session_id, lane_detector.violations
    )
    db.close()

    # Save heatmap
    heatmap_path = "data/outputs/heatmap.jpg"
    heatmap.save(heatmap_path, background=last_frame)

    st.success(f"Session {analytics.session_id} saved to database!")

    # Show heatmap
    st.subheader("Traffic Heatmap")
    st.image(heatmap_path, use_container_width=True)

    # Show summary
    st.subheader("Session Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Frames", summary["total_frames"])
    col2.metric("Vehicles Counted", summary["total_vehicles_counted"])
    col3.metric("Unique IDs", summary["unique_vehicles_tracked"])
    col4.metric("Violations", summary["total_violations"])