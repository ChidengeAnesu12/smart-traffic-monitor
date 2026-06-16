"""
Traffic Density Analysis Module
Measures real-time congestion level based on vehicle count in frame.
Tracks density over time for trend analysis.
"""

import logging
from collections import deque
from typing import List
import time

logger = logging.getLogger(__name__)

# Congestion level thresholds
DENSITY_LEVELS = [
    (0.0, 0.3,  "LOW",       (0, 255, 0)),      # green
    (0.3, 0.6,  "MODERATE",  (0, 255, 255)),     # yellow
    (0.6, 0.8,  "HIGH",      (0, 165, 255)),     # orange
    (0.8, 1.01, "CONGESTED", (0, 0, 255)),       # red
]


class TrafficDensityAnalyzer:
    """
    Analyzes traffic density from tracked vehicle counts.

    Maintains a rolling window of density scores for
    smoothing and trend analysis.
    """

    def __init__(self, config: dict):
        self.config = config
        self.threshold = config["analytics"]["congestion_threshold"]
        self.window_size = 30  # frames to average over

        # Rolling window of vehicle counts
        self.count_history = deque(maxlen=self.window_size)

        # Full history for analytics (frame, count, density, level)
        self.full_history = []

        self.frame_number = 0

        logger.info(
            f"TrafficDensityAnalyzer initialized | "
            f"threshold={self.threshold} vehicles"
        )

    def update(self, tracked_objects: List[dict]) -> dict:
        """
        Update density analysis with current frame's tracked objects.

        Args:
            tracked_objects: list from VehicleTracker.update()

        Returns:
            Density report dict
        """
        vehicle_count = len(tracked_objects)
        self.count_history.append(vehicle_count)
        self.frame_number += 1

        # Smoothed count (average over rolling window)
        smoothed_count = sum(self.count_history) / len(self.count_history)

        # Density score (0.0 to 1.0)
        density_score = min(smoothed_count / self.threshold, 1.0)

        # Congestion level
        level, color = self._get_level(density_score)

        report = {
            "frame": self.frame_number,
            "vehicle_count": vehicle_count,
            "smoothed_count": round(smoothed_count, 2),
            "density_score": round(density_score, 3),
            "level": level,
            "color": color,
        }

        # Store in full history
        self.full_history.append({
            "frame": self.frame_number,
            "count": vehicle_count,
            "density": round(density_score, 3),
            "level": level,
        })

        return report

    def _get_level(self, density_score: float):
        """Map density score to congestion level and color."""
        for low, high, label, color in DENSITY_LEVELS:
            if low <= density_score < high:
                return label, color
        return "CONGESTED", (0, 0, 255)

    def get_summary(self) -> dict:
        """Return summary statistics over the full video."""
        if not self.full_history:
            return {}

        counts = [h["count"] for h in self.full_history]
        densities = [h["density"] for h in self.full_history]

        level_counts = {}
        for h in self.full_history:
            level_counts[h["level"]] = level_counts.get(h["level"], 0) + 1

        # Most common level
        dominant_level = max(level_counts, key=level_counts.get)

        return {
            "total_frames": len(self.full_history),
            "avg_vehicles": round(sum(counts) / len(counts), 2),
            "max_vehicles": max(counts),
            "min_vehicles": min(counts),
            "avg_density": round(sum(densities) / len(densities), 3),
            "peak_density": max(densities),
            "dominant_level": dominant_level,
            "level_distribution": level_counts,
        }