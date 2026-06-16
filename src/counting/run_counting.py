"""
Run vehicle detection + tracking + counting on a video file.
Counts vehicles crossing a virtual line with direction tracking.
"""

import sys
import logging
import yaml
import cv2
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict

sys.path.append(str(Path(__file__).resolve().parents[1]))

from detection.detector import VehicleDetector
from detection.utils import draw_tracks, draw_stats, draw_counting_line, resize_frame
from tracking.tracker import VehicleTracker
from counting.counter import VehicleCounter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_counting(config: dict) -> None:
    video_path = config["video"]["source"]
    output_path = "data/outputs/counting_output.mp4"
    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    detector = VehicleDetector(config)
    tracker = VehicleTracker(config)
    counter = VehicleCounter(config, frame_height)

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

    logger.info(f"Processing {total_frames} frames from {video_path}")
    logger.info(f"Counting line at y={counter.line_y}px")

    frame_count = 0

    with tqdm(total=total_frames, desc="Counting vehicles") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)

            # Step 1: Detect
            detections = detector.detect(frame)

            # Step 2: Track
            tracked_objects = tracker.update(detections, frame)

            # Step 3: Count
            counts = counter.update(tracked_objects)

            # Step 4: Draw
            annotated = draw_tracks(frame, tracked_objects)
            annotated = draw_counting_line(annotated, counter.line_y, counts["total"])
            annotated = draw_stats(annotated, {
                "Total":  counts["total"],
                "Up":     counts["up"],
                "Down":   counts["down"],
            })

            writer.write(annotated)
            frame_count += 1
            pbar.update(1)

    cap.release()
    writer.release()

    # Final summary
    final_counts = counter.get_counts()
    logger.info("=" * 40)
    logger.info("FINAL COUNT SUMMARY")
    logger.info("=" * 40)
    logger.info(f"Total vehicles counted : {final_counts['total']}")
    logger.info(f"Direction UP           : {final_counts['up']}")
    logger.info(f"Direction DOWN         : {final_counts['down']}")
    logger.info("By vehicle type:")
    for vtype, count in final_counts["by_type"].items():
        logger.info(f"  {vtype:<15}: {count}")
    logger.info("=" * 40)
    logger.info(f"Output saved: {output_path}")


def main():
    config = load_config()
    run_counting(config)


if __name__ == "__main__":
    main()