"""
Run full pipeline with lane violation detection.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_lane_violation(config: dict) -> None:
    video_path = config["video"]["source"]
    output_path = "data/outputs/lane_violation_output.mp4"
    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    detector = VehicleDetector(config)
    tracker = VehicleTracker(config)
    counter = VehicleCounter(config, frame_height)
    density_analyzer = TrafficDensityAnalyzer(config)
    speed_estimator = SpeedEstimator(config, fps)
    lane_detector = LaneViolationDetector(config, frame_width)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        output_path, fourcc, fps, (frame_width, frame_height)
    )

    logger.info(f"Processing {total_frames} frames")

    frame_count = 0

    with tqdm(total=total_frames, desc="Detecting violations") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)

            # Pipeline
            detections = detector.detect(frame)
            tracked_objects = tracker.update(detections, frame)
            tracked_with_speed = speed_estimator.update(tracked_objects)
            tracked_with_violations = lane_detector.update(
                tracked_with_speed, frame_count
            )
            counts = counter.update(tracked_objects)
            density_report = density_analyzer.update(tracked_objects)

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

    # Summary
    summary = lane_detector.get_summary()
    logger.info("=" * 40)
    logger.info("LANE VIOLATION SUMMARY")
    logger.info("=" * 40)
    logger.info(f"Total violations : {summary['total_violations']}")
    for vtype, count in summary.get("by_type", {}).items():
        logger.info(f"  {vtype:<20}: {count}")
    logger.info("=" * 40)
    logger.info(f"Output saved: {output_path}")


def main():
    config = load_config()
    run_lane_violation(config)


if __name__ == "__main__":
    main()