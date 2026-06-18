"""
Tests for VehicleTracker module.
"""

import sys
import pytest
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from tracking.tracker import VehicleTracker


@pytest.fixture
def config():
    return {
        "tracking": {
            "max_age": 30,
            "min_hits": 3,
            "iou_threshold": 0.3,
        }
    }


@pytest.fixture
def tracker(config):
    return VehicleTracker(config)


def test_tracker_initializes(tracker):
    """Tracker should initialize without errors."""
    assert tracker is not None


def test_update_returns_list(tracker):
    """update() should always return a list."""
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    result = tracker.update([], blank_frame)
    assert isinstance(result, list)


def test_empty_detections(tracker):
    """Empty detections should return empty tracks."""
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    result = tracker.update([], blank_frame)
    assert result == []


def test_tracker_reset(tracker):
    """Reset should clear all tracks."""
    tracker.reset()
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    result = tracker.update([], blank_frame)
    assert result == []


def test_tracked_object_structure(tracker):
    """Tracked objects should have required keys."""
    blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    detections = [
        {"bbox": [100, 100, 200, 200], "confidence": 0.9, "label": "car"}
    ]
    results = tracker.update(detections, blank_frame)
    for obj in results:
        assert "track_id" in obj
        assert "bbox" in obj
        assert "label" in obj
        assert "confidence" in obj