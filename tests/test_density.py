"""
Tests for TrafficDensityAnalyzer module.
"""

import sys
import pytest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from analytics.density import TrafficDensityAnalyzer


@pytest.fixture
def config():
    return {
        "analytics": {
            "congestion_threshold": 10,
            "speed_limit_kmh": 60,
        }
    }


@pytest.fixture
def analyzer(config):
    return TrafficDensityAnalyzer(config)


def test_analyzer_initializes(analyzer):
    assert analyzer is not None
    assert analyzer.threshold == 10


def test_empty_update(analyzer):
    """Empty frame should return LOW density."""
    report = analyzer.update([])
    assert report["vehicle_count"] == 0
    assert report["level"] == "LOW"
    assert report["density_score"] == 0.0


def test_density_score_range(analyzer):
    """Density score should always be between 0 and 1."""
    objects = [
        {"track_id": i, "bbox": [0, 0, 10, 10], "label": "car"}
        for i in range(20)
    ]
    report = analyzer.update(objects)
    assert 0.0 <= report["density_score"] <= 1.0


def test_congestion_level(analyzer):
    """10+ vehicles should trigger CONGESTED level."""
    objects = [
        {"track_id": i, "bbox": [0, 0, 10, 10], "label": "car"}
        for i in range(15)
    ]
    # Fill rolling window
    for _ in range(30):
        report = analyzer.update(objects)
    assert report["level"] == "CONGESTED"


def test_summary_structure(analyzer):
    """Summary should have required keys."""
    analyzer.update([])
    summary = analyzer.get_summary()
    assert "total_frames" in summary
    assert "avg_vehicles" in summary
    assert "dominant_level" in summary