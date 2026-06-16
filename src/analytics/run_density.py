"""
Run full pipeline: detection + tracking + counting + density analysis.
Saves annotated output and prints summary report.
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
    draw_tracks, draw_stats,
    draw_counting_line, draw_density,
    resize_frame
)
from tracking.tracker import VehicleTracker
from counting.counter import VehicleCounter
from analytics.density import TrafficDensityAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_density_analysis(config: dict) -> None:
    video_path = config["video"]["source"]
    output_path = "data/outputs/density_output.mp4"
    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    detector = VehicleDetector(config)
    tracker = VehicleTracker(config)
    counter = VehicleCounter(config, frame_height)
    density_analyzer = TrafficDensityAnalyzer(config)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        output_path, fourcc, fps, (frame_width, frame_height)
    )

    logger.info(f"Processing {total_frames} frames")

    frame_count = 0

    with tqdm(total=total_frames, desc="Analyzing density") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)

            # Pipeline
            detections = detector.detect(frame)
            tracked_objects = tracker.update(detections, frame)
            counts = counter.update(tracked_objects)
            density_report = density_analyzer.update(tracked_objects)

            # Draw all layers
            annotated = draw_tracks(frame, tracked_objects)
            annotated = draw_counting_line(
                annotated, counter.line_y, counts["total"]
            )
            annotated = draw_density(annotated, density_report)
            annotated = draw_stats(annotated, {
                "Vehicles": density_report["vehicle_count"],
                "Density":  f"{density_report['density_score']:.0%}",
                "Level":    density_report["level"],
                "Counted":  counts["total"],
            })

            writer.write(annotated)
            frame_count += 1
            pbar.update(1)

    cap.release()
    writer.release()

    # Print summary
    summary = density_analyzer.get_summary()
    logger.info("=" * 40)
    logger.info("TRAFFIC DENSITY SUMMARY")
    logger.info("=" * 40)
    logger.info(f"Total frames analyzed : {summary['total_frames']}")
    logger.info(f"Avg vehicles/frame    : {summary['avg_vehicles']}")
    logger.info(f"Peak vehicles/frame   : {summary['max_vehicles']}")
    logger.info(f"Avg density score     : {summary['avg_density']}")
    logger.info(f"Peak density score    : {summary['peak_density']}")
    logger.info(f"Dominant level        : {summary['dominant_level']}")
    logger.info("Level distribution:")
    for level, count in summary["level_distribution"].items():
        logger.info(f"  {level:<12}: {count} frames")
    logger.info("=" * 40)
    logger.info(f"Output saved: {output_path}")


def main():
    config = load_config()
    run_density_analysis(config)


if __name__ == "__main__":
    main()