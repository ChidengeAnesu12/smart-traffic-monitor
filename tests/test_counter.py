"""
Tests for VehicleCounter module.
"""

import sys
import pytest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from counting.counter import VehicleCounter


@pytest.fixture
def config():
    return {
        "counting": {
            "line_position": 0.5,
        }
    }


@pytest.fixture
def counter(config):
    return VehicleCounter(config, frame_height=720)


def test_counter_initializes(counter):
    """Counter should initialize with correct line position."""
    assert counter is not None
    assert counter.line_y == 360  # 720 * 0.5


def test_initial_counts_zero(counter):
    """All counts should start at zero."""
    counts = counter.get_counts()
    assert counts["total"] == 0
    assert counts["up"] == 0
    assert counts["down"] == 0


def test_update_returns_dict(counter):
    """update() should return a dict."""
    result = counter.update([])
    assert isinstance(result, dict)
    assert "total" in result
    assert "up" in result
    assert "down" in result


def test_vehicle_counted_once(counter):
    """Same vehicle should only be counted once."""
    # Simulate vehicle moving downward across line_y=360
    obj = {
        "track_id": 1,
        "bbox": [100, 300, 200, 350],  # above line
        "label": "car",
        "confidence": 0.9,
    }
    counter.update([obj])

    obj["bbox"] = [100, 370, 200, 420]  # below line
    counter.update([obj])

    obj["bbox"] = [100, 400, 200, 450]  # further below
    counter.update([obj])

    counts = counter.get_counts()
    assert counts["total"] == 1


def test_counter_reset(counter):
    """Reset should clear all counts."""
    counter.reset()
    counts = counter.get_counts()
    assert counts["total"] == 0


def test_direction_down(counter):
    """Vehicle moving down should increment down count."""
    obj = {
        "track_id": 2,
        "bbox": [100, 300, 200, 350],
        "label": "car",
        "confidence": 0.9,
    }
    counter.update([obj])
    obj["bbox"] = [100, 370, 200, 420]
    counter.update([obj])

    counts = counter.get_counts()
    assert counts["down"] == 1
    assert counts["up"] == 0