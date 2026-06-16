"""
Vehicle Detector Module
Wraps YOLOv8 for vehicle detection in traffic video frames.
"""

import logging
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class VehicleDetector:
    """
    YOLOv8-based vehicle detector.

    Detects vehicles in frames and returns structured detection results.
    Filters detections to only include vehicle classes defined in config.
    """

    def __init__(self, config: dict):
        self.config = config
        self.model_path = config["model"]["weights"]
        self.confidence = config["model"]["confidence"]
        self.iou_threshold = config["model"]["iou_threshold"]
        self.device = config["model"]["device"]
        self.vehicle_ids = config["classes"]["vehicle_ids"]
        self.labels = {int(k): v for k, v in config["classes"]["labels"].items()}

        self.model = self._load_model()
        logger.info(f"VehicleDetector initialized | model={self.model_path} | device={self.device}")

    def _load_model(self) -> YOLO:
        """Load YOLOv8 model. Downloads automatically if not found."""
        logger.info(f"Loading model: {self.model_path}")
        model = YOLO(self.model_path)
        model.to(self.device)
        return model

    def detect(self, frame: np.ndarray) -> List[dict]:
        """
        Run detection on a single frame.

        Args:
            frame: BGR image as numpy array (from OpenCV)

        Returns:
            List of detections, each as:
            {
                "bbox": [x1, y1, x2, y2],
                "confidence": float,
                "class_id": int,
                "label": str
            }
        """
        results = self.model(
            frame,
            conf=self.confidence,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )

        detections = []

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                class_id = int(box.cls[0])

                if class_id not in self.vehicle_ids:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                label = self.labels.get(class_id, "vehicle")

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": confidence,
                    "class_id": class_id,
                    "label": label,
                })

        return detections

    def detect_batch(self, frames: List[np.ndarray]) -> List[List[dict]]:
        """Run detection on a batch of frames."""
        return [self.detect(frame) for frame in frames]
