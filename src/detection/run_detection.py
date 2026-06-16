"""
Run vehicle detection on a video file.
Saves annotated output video to data/outputs/
"""

import cv2
import yaml
import logging
import sys
from pathlib import Path
from tqdm import tqdm


from utils import draw_detections, draw_stats, resize_frame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_detection(config: dict) -> None:
    video_path = config["video"]["source"]
    output_path = config["video"]["output_path"]
    frame_width = config["video"]["frame_width"]
    frame_height = config["video"]["frame_height"]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    from detector import VehicleDetector
    detector = VehicleDetector(config)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    logger.info(f"Processing {total_frames} frames from {video_path}")

    frame_count = 0
    total_detections = 0

    with tqdm(total=total_frames, desc="Detecting vehicles") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = resize_frame(frame, frame_width, frame_height)
            detections = detector.detect(frame)
            total_detections += len(detections)

            annotated = draw_detections(frame, detections)
            annotated = draw_stats(annotated, {
                "Frame": frame_count,
                "Vehicles": len(detections),
            })

            writer.write(annotated)
            frame_count += 1
            pbar.update(1)

    cap.release()
    writer.release()

    logger.info(f"Done! Processed {frame_count} frames")
    logger.info(f"Total detections: {total_detections}")
    logger.info(f"Output saved: {output_path}")


def main():
    config = load_config()
    run_detection(config)


if __name__ == "__main__":
    main()