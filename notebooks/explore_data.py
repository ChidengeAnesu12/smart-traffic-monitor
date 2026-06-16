"""
Data exploration script.
Run this to inspect any traffic video before processing.
"""

import cv2
import sys
import yaml
from pathlib import Path


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def explore_video(video_path: str) -> dict:
    """Extract and print metadata from a video file."""
    path = Path(video_path)

    if not path.exists():
        print(f"ERROR: File not found: {video_path}")
        sys.exit(1)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        sys.exit(1)

    stats = {
        "file": path.name,
        "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": round(cap.get(cv2.CAP_PROP_FPS), 2),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }

    stats["duration_seconds"] = round(stats["total_frames"] / stats["fps"], 2)

    cap.release()
    return stats


def print_stats(stats: dict) -> None:
    print("\n" + "=" * 40)
    print("   VIDEO METADATA")
    print("=" * 40)
    for key, value in stats.items():
        print(f"  {key:<20}: {value}")
    print("=" * 40 + "\n")


def preview_frames(video_path: str, num_frames: int = 3) -> None:
    """Save sample frames from the video for inspection."""
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    output_dir = Path("data/processed/sample_frames")
    output_dir.mkdir(parents=True, exist_ok=True)

    intervals = [int(total * i / (num_frames + 1)) for i in range(1, num_frames + 1)]

    for idx, frame_num in enumerate(intervals):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if ret:
            out_path = output_dir / f"frame_{idx+1}.jpg"
            cv2.imwrite(str(out_path), frame)
            print(f"Saved sample frame: {out_path}")

    cap.release()


def main():
    config = load_config()
    video_path = config["video"]["source"]

    print(f"Exploring: {video_path}")
    stats = explore_video(video_path)
    print_stats(stats)
    preview_frames(video_path)
    print("Exploration complete. Check data/processed/sample_frames/")


if __name__ == "__main__":
    main()