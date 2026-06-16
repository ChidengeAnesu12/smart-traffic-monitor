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

def draw_tracks(frame: np.ndarray, tracked_objects: List[dict]) -> np.ndarray:
    """
    Draw tracked vehicles with their persistent IDs.

    Args:
        frame: BGR image
        tracked_objects: list of tracked object dicts from VehicleTracker

    Returns:
        Annotated frame
    """
    annotated = frame.copy()

    for obj in tracked_objects:
        x1, y1, x2, y2 = obj["bbox"]
        track_id = obj["track_id"]
        label = obj["label"]
        confidence = obj["confidence"]
        color = CLASS_COLORS.get(label, (255, 255, 0))

        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        # Draw ID + label
        text = f"ID{track_id} {label}"
        (text_w, text_h), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
        )
        cv2.rectangle(
            annotated,
            (x1, y1 - text_h - 8),
            (x1 + text_w + 4, y1),
            color, -1
        )
        cv2.putText(
            annotated, text,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55, (0, 0, 0), 2, cv2.LINE_AA
        )

    return annotated

def draw_counting_line(frame: np.ndarray, line_y: int, count: int) -> np.ndarray:
    """
    Draw the counting line and total count on the frame.

    Args:
        frame: BGR image
        line_y: y-coordinate of counting line
        count: total vehicles counted so far

    Returns:
        Annotated frame
    """
    annotated = frame.copy()
    width = frame.shape[1]

    # Draw the counting line
    cv2.line(
        annotated,
        (0, line_y),
        (width, line_y),
        (0, 255, 255),  # yellow
        2
    )

    # Draw count label on line
    text = f"COUNT LINE | Total: {count}"
    cv2.putText(
        annotated, text,
        (10, line_y - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6, (0, 255, 255), 2, cv2.LINE_AA
    )

    return annotated

def draw_density(frame: np.ndarray, density_report: dict) -> np.ndarray:
    """
    Draw traffic density indicator on the frame.

    Args:
        frame: BGR image
        density_report: dict from TrafficDensityAnalyzer.update()

    Returns:
        Annotated frame
    """
    annotated = frame.copy()
    h, w = annotated.shape[:2]

    level = density_report["level"]
    score = density_report["density_score"]
    color = density_report["color"]

    # Draw density bar background (bottom right)
    bar_x = w - 220
    bar_y = h - 60
    cv2.rectangle(annotated, (bar_x, bar_y), (w - 10, h - 10), (30, 30, 30), -1)

    # Draw filled portion of bar
    bar_width = int(190 * score)
    cv2.rectangle(
        annotated,
        (bar_x + 5, bar_y + 5),
        (bar_x + 5 + bar_width, h - 15),
        color, -1
    )

    # Draw level text
    cv2.putText(
        annotated,
        f"{level} ({score:.0%})",
        (bar_x + 5, bar_y - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6, color, 2, cv2.LINE_AA
    )

    return annotated

def draw_speed(frame: np.ndarray, tracked_objects: List[dict]) -> np.ndarray:
    """
    Draw speed labels on tracked vehicles.

    Args:
        frame: BGR image
        tracked_objects: list with speed_kmh and speeding fields

    Returns:
        Annotated frame
    """
    annotated = frame.copy()

    for obj in tracked_objects:
        speed = obj.get("speed_kmh")
        if speed is None:
            continue

        x1, y1, x2, y2 = obj["bbox"]
        speeding = obj.get("speeding", False)

        # Red if speeding, white if normal
        color = (0, 0, 255) if speeding else (255, 255, 255)
        text = f"{speed} km/h"
        if speeding:
            text += " !"

        cv2.putText(
            annotated, text,
            (x1, y2 + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55, color, 2, cv2.LINE_AA
        )

    return annotated