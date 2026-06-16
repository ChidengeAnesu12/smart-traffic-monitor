"""
Detection utility functions.
Drawing bounding boxes, labels, and overlays on frames.
"""

import cv2
import numpy as np
from typing import List

# Color map per vehicle class
CLASS_COLORS = {
    "car":        (0, 255, 0),      # green
    "motorcycle": (255, 165, 0),    # orange
    "bus":        (0, 0, 255),      # red
    "truck":      (255, 0, 255),    # magenta
    "vehicle":    (255, 255, 0),    # yellow (fallback)
}


def draw_detections(frame: np.ndarray, detections: List[dict]) -> np.ndarray:
    """
    Draw bounding boxes and labels on a frame.

    Args:
        frame: BGR image
        detections: list of detection dicts from VehicleDetector

    Returns:
        Annotated frame
    """
    annotated = frame.copy()

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = det["label"]
        confidence = det["confidence"]
        color = CLASS_COLORS.get(label, (255, 255, 0))

        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        # Draw label background
        text = f"{label} {confidence:.2f}"
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x1, y1 - text_h - 6), (x1 + text_w, y1), color, -1)

        # Draw label text
        cv2.putText(
            annotated, text,
            (x1, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 0), 1, cv2.LINE_AA
        )

    return annotated


def draw_stats(frame: np.ndarray, stats: dict) -> np.ndarray:
    """
    Draw stats overlay in top-left corner.

    Args:
        frame: BGR image
        stats: dict of stat name -> value
    """
    annotated = frame.copy()
    x, y = 10, 30
    line_height = 25

    for key, value in stats.items():
        text = f"{key}: {value}"
        cv2.putText(
            annotated, text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 255), 2, cv2.LINE_AA
        )
        y += line_height

    return annotated


def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize frame to target dimensions."""
    return cv2.resize(frame, (width, height))