"""
Tests for VehicleDetector module.
Run with: python -m pytest tests/ -v
"""

import sys
import pytest
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from detection.detector import VehicleDetector


@pytest.fixture
def config():
    return {
        "model": {
            "weights": "yolov8n.pt",
            "confidence": 0.4,
            "iou_threshold": 0.5,
            "device": "cpu",
        },
        "classes": {
            "vehicle_ids": [2, 3, 5, 7],
            "labels": {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"},
        },
    }


@pytest.fixture
def detector(config):
    return VehicleDetector(config)


def test_detector_initializes(detector):
    """Detector should initialize without errors."""
    assert detector is not None
    assert detector.model is not None


def test_detect_returns_list(detector):
    """detect() should always return a list."""
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    result = detector.detect(blank_frame)
    assert isinstance(result, list)


def test_detect_empty_frame(detector):
    """Blank frame should return empty detections."""
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    result = detector.detect(blank_frame)
    assert result == []


def test_detection_structure(detector):
    """Each detection should have required keys."""
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    results = detector.detect(blank_frame)
    for det in results:
        assert "bbox" in det
        assert "confidence" in det
        assert "class_id" in det
        assert "label" in det
        assert len(det["bbox"]) == 4


def test_confidence_filter(config):
    """High confidence threshold should reduce detections."""
    config["model"]["confidence"] = 0.99
    detector_strict = VehicleDetector(config)
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    result = detector_strict.detect(blank_frame)
    assert result == []
