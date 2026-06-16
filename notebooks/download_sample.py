"""
Download a sample traffic video for testing.
Run this script once to get a test video.
"""

import urllib.request
import os
from pathlib import Path


SAMPLE_VIDEOS = [
    {
        "name": "sample_traffic.mp4",
        "url": "https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4",
    }
]


def download_sample(url: str, save_path: str) -> None:
    """Download a sample video with progress reporting."""
    print(f"Downloading: {url}")
    print(f"Saving to: {save_path}")

    def progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        print(f"\rProgress: {percent:.1f}%", end="", flush=True)

    urllib.request.urlretrieve(url, save_path, reporthook=progress)
    print("\nDone!")


def main():
    save_dir = Path("data/raw")
    save_dir.mkdir(parents=True, exist_ok=True)

    for video in SAMPLE_VIDEOS:
        save_path = save_dir / video["name"]
        if save_path.exists():
            print(f"Already exists: {save_path}")
            continue
        download_sample(video["url"], str(save_path))

    print("\nAll samples ready in data/raw/")


if __name__ == "__main__":
    main()