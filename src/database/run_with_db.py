"""
Full pipeline with database integration.
All analytics data is persisted to SQLite.
"""

import sys
import logging
import yaml
import cv2
from pathlib import Path
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parents[1]))

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_pipeline_with_db(config: dict) -> None:
    video_path = config["video"]["source"]
    output_path = "data/outputs/db_pipeline_output.mp4"
    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Initialize all modules
    detector = VehicleDetector(config)
    tracker = VehicleTracker(config)
    counter = VehicleCounter(config, frame_height)
    density_analyzer = TrafficDensityAnalyzer(config)
    speed_estimator = SpeedEstimator(config, fps)
    lane_detector = LaneViolationDetector(config, frame_width)
    heatmap = TrafficHeatmap(frame_width, frame_height)
    analytics = AnalyticsEngine(config)
    db = DatabaseHandler(config)

    # Create session in DB
    db.create_session(analytics.session_id, video_path)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        output_path, fourcc, fps, (frame_width, frame_height)
    )

    logger.info(f"Processing {total_frames} frames")
    logger.info(f"Session ID: {analytics.session_id}")

    frame_count = 0
    last_frame = None

    with tqdm(total=total_frames, desc="Pipeline + DB") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)
            last_frame = frame.copy()

            # Full pipeline
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
                frame_count,
                tracked_with_violations,
                density_report,
                counts,
            )

            # Draw all layers
            annotated = draw_zones(frame, lane_detector.zones)
            annotated = draw_tracks(annotated, tracked_with_violations)
            annotated = draw_speed(annotated, tracked_with_violations)
            annotated = draw_violations(annotated, tracked_with_violations)
            annotated = draw_counting_line(
                annotated, counter.line_y, counts["total"]
            )
            annotated = draw_density(annotated, density_report)
            annotated = draw_stats(annotated, {
                "Vehicles":   density_report["vehicle_count"],
                "Level":      density_report["level"],
                "Counted":    counts["total"],
                "Violations": len(lane_detector.violations),
            })

            writer.write(annotated)
            frame_count += 1
            pbar.update(1)

    cap.release()
    writer.release()

    # Save heatmap
    heatmap.save("data/outputs/heatmap.jpg", background=last_frame)

    # Save to database
    summary = analytics.get_summary()
    db.update_session(analytics.session_id, summary)
    db.insert_frame_records(analytics.session_id, analytics.frame_records)
    db.insert_vehicles(analytics.session_id, analytics.vehicle_records)
    db.insert_violations(
        analytics.session_id, lane_detector.violations
    )
    db.close()

    # Print summary
    analytics.print_summary()

    logger.info("=" * 45)
    logger.info(f"Database     : {config['database']['path']}")
    logger.info(f"Output video : {output_path}")
    logger.info("=" * 45)


def main():
    config = load_config()
    run_pipeline_with_db(config)


if __name__ == "__main__":
    main()