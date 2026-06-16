"""
Vehicle Counter Module
Counts vehicles crossing a virtual line in the video frame.
Tracks direction (up/down) and vehicle type.
"""

import logging
from typing import List, Dict, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class VehicleCounter:
    """
    Counts vehicles crossing a defined line in the frame.

    Logic:
    - Each tracked vehicle has a center point (cx, cy)
    - We record the center position every frame
    - When the center crosses the counting line, we count it
    - Each track ID is only counted once
    """

    def __init__(self, config: dict, frame_height: int):
        self.config = config
        self.line_position = config["counting"]["line_position"]

        # Counting line y-coordinate in pixels
        self.line_y = int(frame_height * self.line_position)

        # Track previous center positions {track_id: (cx, cy)}
        self.previous_positions: Dict[int, Tuple[int, int]] = {}

        # Track IDs already counted
        self.counted_ids: set = set()

        # Counts per direction and vehicle type
        self.counts = {
            "total": 0,
            "up": 0,
            "down": 0,
            "by_type": defaultdict(int),
        }

        logger.info(
            f"VehicleCounter initialized | "
            f"line_y={self.line_y}px | "
            f"line_position={self.line_position}"
        )

    def update(self, tracked_objects: List[dict]) -> dict:
        """
        Update counter with current frame's tracked objects.

        Args:
            tracked_objects: list from VehicleTracker.update()

        Returns:
            Current counts dict
        """
        for obj in tracked_objects:
            track_id = obj["track_id"]
            x1, y1, x2, y2 = obj["bbox"]
            label = obj["label"]

            # Calculate center point
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Skip if already counted
            if track_id in self.counted_ids:
                self.previous_positions[track_id] = (cx, cy)
                continue

            # Check if we have a previous position
            if track_id in self.previous_positions:
                prev_cx, prev_cy = self.previous_positions[track_id]

                # Check if center crossed the counting line
                crossed_down = prev_cy < self.line_y <= cy
                crossed_up = prev_cy > self.line_y >= cy

                if crossed_down:
                    self.counts["total"] += 1
                    self.counts["down"] += 1
                    self.counts["by_type"][label] += 1
                    self.counted_ids.add(track_id)
                    logger.debug(
                        f"Vehicle counted | ID={track_id} | "
                        f"type={label} | direction=down"
                    )

                elif crossed_up:
                    self.counts["total"] += 1
                    self.counts["up"] += 1
                    self.counts["by_type"][label] += 1
                    self.counted_ids.add(track_id)
                    logger.debug(
                        f"Vehicle counted | ID={track_id} | "
                        f"type={label} | direction=up"
                    )

            # Update previous position
            self.previous_positions[track_id] = (cx, cy)

        return self.get_counts()

    def get_counts(self) -> dict:
        """Return current count summary."""
        return {
            "total": self.counts["total"],
            "up": self.counts["up"],
            "down": self.counts["down"],
            "by_type": dict(self.counts["by_type"]),
        }

    def reset(self) -> None:
        """Reset all counts — use when switching video sources."""
        self.previous_positions.clear()
        self.counted_ids.clear()
        self.counts = {
            "total": 0,
            "up": 0,
            "down": 0,
            "by_type": defaultdict(int),
        }
        logger.info("VehicleCounter reset.")