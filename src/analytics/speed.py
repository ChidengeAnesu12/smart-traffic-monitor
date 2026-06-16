"""
Vehicle Speed Estimation Module
Estimates vehicle speed using pixel displacement between frames.
Uses a pixel-to-meter scale factor for real-world conversion.
"""

import logging
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default calibration:
# Assumes average lane width of 3.5 meters = ~150 pixels at typical camera angle
DEFAULT_PIXELS_PER_METER = 8.0


class SpeedEstimator:
    """
    Estimates vehicle speed from frame-to-frame pixel displacement.

    Maintains position history per track ID and computes
    speed using pixel-to-meter calibration.
    """

    def __init__(self, config: dict, fps: float):
        self.config = config
        self.fps = fps
        self.speed_limit = config["analytics"]["speed_limit_kmh"]

        # Calibration: pixels per meter
        self.pixels_per_meter = DEFAULT_PIXELS_PER_METER

        # Position history per track: {track_id: deque of (frame, cx, cy)}
        self.position_history: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=10)
        )

        # Smoothed speed per track: {track_id: deque of speeds}
        self.speed_history: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=5)
        )

        # Final speed record per track
        self.speed_records: Dict[int, dict] = {}

        self.frame_number = 0

        logger.info(
            f"SpeedEstimator initialized | "
            f"fps={fps} | "
            f"pixels_per_meter={self.pixels_per_meter} | "
            f"speed_limit={self.speed_limit}km/h"
        )

    def update(self, tracked_objects: List[dict]) -> List[dict]:
        """
        Update speed estimates for all tracked vehicles.

        Args:
            tracked_objects: list from VehicleTracker.update()

        Returns:
            tracked_objects with 'speed_kmh' and 'speeding' added
        """
        self.frame_number += 1
        results = []

        for obj in tracked_objects:
            track_id = obj["track_id"]
            x1, y1, x2, y2 = obj["bbox"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Store current position
            self.position_history[track_id].append(
                (self.frame_number, cx, cy)
            )

            # Need at least 2 positions to estimate speed
            speed_kmh = self._estimate_speed(track_id)

            # Smooth speed using rolling average
            if speed_kmh is not None:
                self.speed_history[track_id].append(speed_kmh)

            smoothed_speed = self._get_smoothed_speed(track_id)
            is_speeding = (
                smoothed_speed > self.speed_limit
                if smoothed_speed is not None
                else False
            )

            # Update speed record
            if smoothed_speed is not None:
                self.speed_records[track_id] = {
                    "track_id": track_id,
                    "label": obj["label"],
                    "speed_kmh": smoothed_speed,
                    "speeding": is_speeding,
                }

            results.append({
                **obj,
                "speed_kmh": smoothed_speed,
                "speeding": is_speeding,
            })

        return results

    def _estimate_speed(self, track_id: int) -> Optional[float]:
        """Calculate speed from position history."""
        history = self.position_history[track_id]

        if len(history) < 2:
            return None

        # Use oldest and newest position in history
        frame_old, cx_old, cy_old = history[0]
        frame_new, cx_new, cy_new = history[-1]

        frames_elapsed = frame_new - frame_old
        if frames_elapsed == 0:
            return None

        # Pixel displacement (Euclidean distance)
        pixel_dist = ((cx_new - cx_old) ** 2 + (cy_new - cy_old) ** 2) ** 0.5

        # Convert to real-world distance
        real_dist_meters = pixel_dist / self.pixels_per_meter

        # Time elapsed
        time_seconds = frames_elapsed / self.fps

        # Speed in km/h
        speed_ms = real_dist_meters / time_seconds
        speed_kmh = speed_ms * 3.6

        return round(speed_kmh, 1)

    def _get_smoothed_speed(self, track_id: int) -> Optional[float]:
        """Return rolling average speed for a track."""
        history = self.speed_history[track_id]
        if not history:
            return None
        return round(sum(history) / len(history), 1)

    def get_summary(self) -> dict:
        """Return speed summary across all tracked vehicles."""
        if not self.speed_records:
            return {}

        speeds = [r["speed_kmh"] for r in self.speed_records.values()]
        speeders = [r for r in self.speed_records.values() if r["speeding"]]

        return {
            "vehicles_tracked": len(self.speed_records),
            "avg_speed_kmh": round(sum(speeds) / len(speeds), 1),
            "max_speed_kmh": max(speeds),
            "min_speed_kmh": min(speeds),
            "speeders_count": len(speeders),
            "speed_limit_kmh": self.speed_limit,
        }