"""
Analytics Engine
Aggregates all analytics data and generates summary reports.
Combines density, speed, counting, and violation data.
"""

import logging
import json
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Central analytics aggregator.
    Collects data from all modules and generates reports.
    """

    def __init__(self, config: dict):
        self.config = config
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Per-frame records
        self.frame_records: List[dict] = []

        # Vehicle-level records
        self.vehicle_records: Dict[int, dict] = {}

        logger.info(f"AnalyticsEngine initialized | session={self.session_id}")

    def record_frame(
        self,
        frame_number: int,
        tracked_objects: List[dict],
        density_report: dict,
        counts: dict,
    ) -> None:
        """Record analytics for a single frame."""
        self.frame_records.append({
            "frame": frame_number,
            "vehicle_count": density_report["vehicle_count"],
            "density_score": density_report["density_score"],
            "density_level": density_report["level"],
            "total_counted": counts["total"],
            "counted_up": counts["up"],
            "counted_down": counts["down"],
        })

        # Update per-vehicle records
        for obj in tracked_objects:
            tid = obj["track_id"]
            if tid not in self.vehicle_records:
                self.vehicle_records[tid] = {
                    "track_id": tid,
                    "label": obj["label"],
                    "first_frame": frame_number,
                    "last_frame": frame_number,
                    "max_speed": None,
                    "avg_speed": None,
                    "violation": None,
                    "zone": obj.get("zone", "unknown"),
                    "speed_samples": [],
                }

            record = self.vehicle_records[tid]
            record["last_frame"] = frame_number
            record["zone"] = obj.get("zone", record["zone"])

            speed = obj.get("speed_kmh")
            if speed is not None:
                record["speed_samples"].append(speed)

            if obj.get("violation"):
                record["violation"] = obj["violation"]

        # Finalize speed stats
        for tid, record in self.vehicle_records.items():
            samples = record["speed_samples"]
            if samples:
                record["max_speed"] = max(samples)
                record["avg_speed"] = round(sum(samples) / len(samples), 1)

    def get_summary(self) -> dict:
        """Generate full analytics summary."""
        if not self.frame_records:
            return {}

        densities = [r["density_score"] for r in self.frame_records]
        counts = [r["vehicle_count"] for r in self.frame_records]

        level_dist = defaultdict(int)
        for r in self.frame_records:
            level_dist[r["density_level"]] += 1

        vehicles = list(self.vehicle_records.values())
        type_counts = defaultdict(int)
        for v in vehicles:
            type_counts[v["label"]] += 1

        violations = [v for v in vehicles if v["violation"]]

        return {
            "session_id": self.session_id,
            "total_frames": len(self.frame_records),
            "total_vehicles_counted": (
                self.frame_records[-1]["total_counted"]
                if self.frame_records else 0
            ),
            "unique_vehicles_tracked": len(self.vehicle_records),
            "avg_density": round(sum(densities) / len(densities), 3),
            "peak_density": max(densities),
            "avg_vehicles_per_frame": round(sum(counts) / len(counts), 2),
            "peak_vehicles_per_frame": max(counts),
            "density_level_distribution": dict(level_dist),
            "vehicle_type_distribution": dict(type_counts),
            "total_violations": len(violations),
        }

    def save_csv(self, output_path: str) -> None:
        """Save frame-level records to CSV."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if not self.frame_records:
            logger.warning("No frame records to save.")
            return

        keys = self.frame_records[0].keys()
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.frame_records)

        logger.info(f"CSV saved: {output_path}")

    def save_json(self, output_path: str) -> None:
        """Save full summary to JSON."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        summary = self.get_summary()

        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"JSON saved: {output_path}")

    def print_summary(self) -> None:
        """Print formatted summary to console."""
        summary = self.get_summary()
        if not summary:
            logger.info("No data to summarize.")
            return

        logger.info("=" * 45)
        logger.info("FULL ANALYTICS SUMMARY")
        logger.info("=" * 45)
        logger.info(f"Session ID          : {summary['session_id']}")
        logger.info(f"Total frames        : {summary['total_frames']}")
        logger.info(f"Vehicles counted    : {summary['total_vehicles_counted']}")
        logger.info(f"Unique IDs tracked  : {summary['unique_vehicles_tracked']}")
        logger.info(f"Avg density         : {summary['avg_density']}")
        logger.info(f"Peak density        : {summary['peak_density']}")
        logger.info(f"Avg vehicles/frame  : {summary['avg_vehicles_per_frame']}")
        logger.info(f"Peak vehicles/frame : {summary['peak_vehicles_per_frame']}")
        logger.info(f"Total violations    : {summary['total_violations']}")
        logger.info("Vehicle types:")
        for vtype, count in summary["vehicle_type_distribution"].items():
            logger.info(f"  {vtype:<15}: {count}")
        logger.info("Density levels:")
        for level, count in summary["density_level_distribution"].items():
            logger.info(f"  {level:<12}: {count} frames")
        logger.info("=" * 45)