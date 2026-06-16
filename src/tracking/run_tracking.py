"""
Run vehicle detection + tracking on a video file.
Each vehicle gets a persistent ID across frames.
"""

import sys
import logging
import yaml
import cv2
from pathlib import Path
from tqdm import tqdm

# Allow imports from src/
sys.path.append(str(Path(__file__).resolve().parents[1]))

from detection.detector import VehicleDetector
from detection.utils import draw_tracks, draw_stats, resize_frame
from tracking.tracker import VehicleTracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_tracking(config: dict) -> None:
    video_path = config["video"]["source"]
    output_path = "data/outputs/tracking_output.mp4"
    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    detector = VehicleDetector(config)
    tracker = VehicleTracker(config)

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

    frame_count = 0
    all_track_ids = set()

    with tqdm(total=total_frames, desc="Tracking vehicles") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)

            # Step 1: Detect
            detections = detector.detect(frame)

            # Step 2: Track
            tracked_objects = tracker.update(detections, frame)

            # Collect unique IDs seen so far
            for obj in tracked_objects:
                all_track_ids.add(obj["track_id"])

            # Step 3: Draw
            annotated = draw_tracks(frame, tracked_objects)
            annotated = draw_stats(annotated, {
                "Frame": frame_count,
                "Tracking": len(tracked_objects),
                "Total IDs": len(all_track_ids),
            })

            writer.write(annotated)
            frame_count += 1
            pbar.update(1)

    cap.release()
    writer.release()

    logger.info(f"Done! Processed {frame_count} frames")
    logger.info(f"Unique vehicles tracked: {len(all_track_ids)}")
    logger.info(f"Output saved: {output_path}")


def main():
    config = load_config()
    run_tracking(config)


if __name__ == "__main__":
    main()
