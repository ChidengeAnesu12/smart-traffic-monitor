"""
Traffic Heatmap Module
Accumulates vehicle positions across frames to generate
a heatmap showing high-traffic areas.
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class TrafficHeatmap:
    """
    Generates a traffic heatmap by accumulating vehicle
    center positions across all video frames.
    """

    def __init__(self, frame_width: int, frame_height: int):
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Accumulator — float32 for precision
        self.accumulator = np.zeros(
            (frame_height, frame_width), dtype=np.float32
        )

        self.frame_count = 0
        self.total_points = 0

        logger.info(
            f"TrafficHeatmap initialized | "
            f"size={frame_width}x{frame_height}"
        )

    def update(self, tracked_objects: List[dict]) -> None:
        """
        Add vehicle positions from current frame to accumulator.

        Args:
            tracked_objects: list from VehicleTracker.update()
        """
        self.frame_count += 1

        for obj in tracked_objects:
            x1, y1, x2, y2 = obj["bbox"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Add a gaussian blob at vehicle center
            self._add_heat(cx, cy, radius=40, intensity=1.0)
            self.total_points += 1

    def _add_heat(
        self,
        cx: int,
        cy: int,
        radius: int = 40,
        intensity: float = 1.0,
    ) -> None:
        """
        Add a gaussian heat blob at (cx, cy).
        Using a filled circle for simplicity and speed.
        """
        # Clamp to frame bounds
        cx = max(radius, min(cx, self.frame_width - radius))
        cy = max(radius, min(cy, self.frame_height - radius))

        # Draw filled circle on accumulator
        cv2.circle(
            self.accumulator,
            (cx, cy),
            radius,
            intensity,
            -1
        )

    def get_heatmap(self) -> np.ndarray:
        """
        Generate the final heatmap image.

        Returns:
            BGR heatmap image (same size as input frames)
        """
        if self.accumulator.max() == 0:
            return np.zeros(
                (self.frame_height, self.frame_width, 3), dtype=np.uint8
            )

        # Normalize to 0-255
        normalized = cv2.normalize(
            self.accumulator, None, 0, 255, cv2.NORM_MINMAX
        )
        normalized = normalized.astype(np.uint8)

        # Apply colormap (JET: blue=cold, red=hot)
        heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)

        return heatmap

    def get_overlay(self, background: np.ndarray, alpha: float = 0.6) -> np.ndarray:
        """
        Overlay heatmap on a background frame.

        Args:
            background: BGR frame to overlay on
            alpha: heatmap opacity (0.0-1.0)

        Returns:
            Blended BGR image
        """
        heatmap = self.get_heatmap()
        return cv2.addWeighted(heatmap, alpha, background, 1 - alpha, 0)

    def save(self, output_path: str, background: np.ndarray = None) -> None:
        """
        Save heatmap to disk.

        Args:
            output_path: file path to save image
            background: optional frame to overlay on
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if background is not None:
            image = self.get_overlay(background)
        else:
            image = self.get_heatmap()

        cv2.imwrite(output_path, image)
        logger.info(f"Heatmap saved: {output_path}")

    def reset(self) -> None:
        """Reset the accumulator."""
        self.accumulator = np.zeros(
            (self.frame_height, self.frame_width), dtype=np.float32
        )
        self.frame_count = 0
        self.total_points = 0