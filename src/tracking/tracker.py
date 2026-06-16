"""
Vehicle Tracker Module
Wraps DeepSORT for multi-object tracking across video frames.
Assigns persistent IDs to detected vehicles.
"""

import logging
from typing import List, Tuple

import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort

logger = logging.getLogger(__name__)


class VehicleTracker:
    """
    DeepSORT-based vehicle tracker.

    Takes detections from VehicleDetector and assigns
    persistent IDs across frames.
    """

    def __init__(self, config: dict):
        self.config = config
        self.max_age = config["tracking"]["max_age"]
        self.min_hits = config["tracking"]["min_hits"]
        self.iou_threshold = config["tracking"]["iou_threshold"]

        self.tracker = DeepSort(
            max_age=self.max_age,
            n_init=self.min_hits,
            max_iou_distance=self.iou_threshold,
        )

        logger.info(
            f"VehicleTracker initialized | "
            f"max_age={self.max_age} | "
            f"min_hits={self.min_hits}"
        )

    def update(self, detections: List[dict], frame: np.ndarray) -> List[dict]:
        """
        Update tracker with new detections from current frame.

        Args:
            detections: list of dicts from VehicleDetector.detect()
            frame: current BGR frame (used for appearance features)

        Returns:
            List of tracked objects:
            {
                "track_id": int,
                "bbox": [x1, y1, x2, y2],
                "label": str,
                "confidence": float,
            }
        """
        if not detections:
            self.tracker.update_tracks([], frame=frame)
            return []

        # Convert detections to DeepSORT format
        # DeepSORT expects: ([x1, y1, w, h], confidence, label)
        ds_detections = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            w = x2 - x1
            h = y2 - y1
            ds_detections.append(
                ([x1, y1, w, h], det["confidence"], det["label"])
            )

        # Update tracker
        tracks = self.tracker.update_tracks(ds_detections, frame=frame)

        # Build output
        tracked_objects = []
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            ltrb = track.to_ltrb()  # [x1, y1, x2, y2]
            x1, y1, x2, y2 = map(int, ltrb)
            label = track.get_det_class() or "vehicle"
            confidence = track.get_det_conf() or 0.0

            tracked_objects.append({
                "track_id": track_id,
                "bbox": [x1, y1, x2, y2],
                "label": label,
                "confidence": confidence if confidence else 0.0,
            })

        return tracked_objects

    def reset(self) -> None:
        """Reset the tracker — use when switching video sources."""
        self.tracker = DeepSort(
            max_age=self.max_age,
            n_init=self.min_hits,
            max_iou_distance=self.iou_threshold,
        )
        logger.info("Tracker reset.")