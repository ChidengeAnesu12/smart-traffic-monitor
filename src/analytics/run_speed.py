"""
Run full pipeline with speed estimation.
Detects, tracks, counts, analyzes density, and estimates speed.
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
    draw_density, draw_speed, resize_frame
)
from tracking.tracker import VehicleTracker
from counting.counter import VehicleCounter
from analytics.density import TrafficDensityAnalyzer
from analytics.speed import SpeedEstimator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_speed_estimation(config: dict) -> None:
    video_path = config["video"]["source"]
    output_path = "data/outputs/speed_output.mp4"
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

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        output_path, fourcc, fps, (frame_width, frame_height)
    )

    logger.info(f"Processing {total_frames} frames")

    frame_count = 0

    with tqdm(total=total_frames, desc="Estimating speeds") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)

            # Pipeline
            detections = detector.detect(frame)
            tracked_objects = tracker.update(detections, frame)
            tracked_with_speed = speed_estimator.update(tracked_objects)
            counts = counter.update(tracked_objects)
            density_report = density_analyzer.update(tracked_objects)

            # Draw all layers
            annotated = draw_tracks(frame, tracked_with_speed)
            annotated = draw_speed(annotated, tracked_with_speed)
            annotated = draw_counting_line(
                annotated, counter.line_y, counts["total"]
            )
            annotated = draw_density(annotated, density_report)
            annotated = draw_stats(annotated, {
                "Vehicles": density_report["vehicle_count"],
                "Level":    density_report["level"],
                "Counted":  counts["total"],
            })

            writer.write(annotated)
            frame_count += 1
            pbar.update(1)

    cap.release()
    writer.release()

    # Summary
    summary = speed_estimator.get_summary()
    if summary:
        logger.info("=" * 40)
        logger.info("SPEED ESTIMATION SUMMARY")
        logger.info("=" * 40)
        logger.info(f"Vehicles tracked  : {summary['vehicles_tracked']}")
        logger.info(f"Avg speed         : {summary['avg_speed_kmh']} km/h")
        logger.info(f"Max speed         : {summary['max_speed_kmh']} km/h")
        logger.info(f"Min speed         : {summary['min_speed_kmh']} km/h")
        logger.info(f"Speed limit       : {summary['speed_limit_kmh']} km/h")
        logger.info(f"Speeders detected : {summary['speeders_count']}")
        logger.info("=" * 40)
    else:
        logger.info("No vehicles tracked long enough for speed estimation.")

    logger.info(f"Output saved: {output_path}")


def main():
    config = load_config()
    run_speed_estimation(config)


if __name__ == "__main__":
    main()