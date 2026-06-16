"""
Lane Violation Detection Module
Uses virtual lane zones to detect lane violations.
Rule-based approach suitable for fixed traffic cameras.
"""

import logging
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# Violation type definitions
VIOLATION_TYPES = {
    "WRONG_LANE":      "Vehicle in wrong lane",
    "LANE_CHANGE":     "Sudden lane change detected",
    "RESTRICTED_ZONE": "Vehicle in restricted zone",
}


class LaneZone:
    """Represents a single lane zone in the frame."""

    def __init__(
        self,
        zone_id: int,
        x_start: int,
        x_end: int,
        label: str,
        restricted: bool = False,
        allowed_direction: Optional[str] = None,
    ):
        self.zone_id = zone_id
        self.x_start = x_start
        self.x_end = x_end
        self.label = label
        self.restricted = restricted          # e.g. emergency lane
        self.allowed_direction = allowed_direction  # "up", "down", or None

    def contains(self, cx: int) -> bool:
        """Check if x-coordinate is within this zone."""
        return self.x_start <= cx < self.x_end

    def __repr__(self):
        return f"LaneZone(id={self.zone_id}, label={self.label})"


class LaneViolationDetector:
    """
    Detects lane violations using virtual zone boundaries.

    Tracks which lane each vehicle is in and flags
    violations based on configurable rules.
    """

    def __init__(self, config: dict, frame_width: int):
        self.config = config
        self.frame_width = frame_width

        # Build lane zones
        self.zones = self._build_zones(frame_width)

        # Track current zone per vehicle {track_id: zone_id}
        self.vehicle_zones: Dict[int, int] = {}

        # Track zone history {track_id: [zone_id, zone_id, ...]}
        self.zone_history: Dict[int, List[int]] = defaultdict(list)

        # Violation log
        self.violations: List[dict] = []

        # Vehicles currently in violation {track_id: violation_type}
        self.active_violations: Dict[int, str] = {}

        logger.info(
            f"LaneViolationDetector initialized | "
            f"frame_width={frame_width} | "
            f"zones={len(self.zones)}"
        )
        for zone in self.zones:
            logger.info(
                f"  Zone {zone.zone_id}: {zone.label} "
                f"x=[{zone.x_start}-{zone.x_end}] "
                f"restricted={zone.restricted}"
            )

    def _build_zones(self, frame_width: int) -> List[LaneZone]:
        """
        Build lane zones based on frame width.
        Divides frame into 4 zones:
        - Emergency/shoulder lane (restricted)
        - Lane 1 (left)
        - Lane 2 (right)
        - Emergency/shoulder lane (restricted)
        """
        w = frame_width
        zones = [
            LaneZone(
                zone_id=0,
                x_start=0,
                x_end=int(w * 0.1),
                label="Shoulder L",
                restricted=True,
            ),
            LaneZone(
                zone_id=1,
                x_start=int(w * 0.1),
                x_end=int(w * 0.5),
                label="Lane 1",
                restricted=False,
                allowed_direction="down",
            ),
            LaneZone(
                zone_id=2,
                x_start=int(w * 0.5),
                x_end=int(w * 0.9),
                label="Lane 2",
                restricted=False,
                allowed_direction="up",
            ),
            LaneZone(
                zone_id=3,
                x_start=int(w * 0.9),
                x_end=w,
                label="Shoulder R",
                restricted=True,
            ),
        ]
        return zones

    def _get_zone(self, cx: int) -> Optional[LaneZone]:
        """Return the zone containing the given x-coordinate."""
        for zone in self.zones:
            if zone.contains(cx):
                return zone
        return None

    def update(
        self, tracked_objects: List[dict], frame_number: int
    ) -> List[dict]:
        """
        Check all tracked vehicles for lane violations.

        Args:
            tracked_objects: list from VehicleTracker.update()
            frame_number: current frame index

        Returns:
            tracked_objects with 'violation' field added
        """
        self.active_violations.clear()
        results = []

        for obj in tracked_objects:
            track_id = obj["track_id"]
            x1, y1, x2, y2 = obj["bbox"]
            cx = (x1 + x2) // 2

            current_zone = self._get_zone(cx)
            violation = None

            if current_zone is not None:
                # Check restricted zone violation
                if current_zone.restricted:
                    violation = "RESTRICTED_ZONE"
                    self._log_violation(
                        track_id, violation,
                        current_zone, frame_number, obj["label"]
                    )

                # Check sudden lane change
                elif track_id in self.vehicle_zones:
                    prev_zone_id = self.vehicle_zones[track_id]
                    if (
                        prev_zone_id != current_zone.zone_id
                        and abs(prev_zone_id - current_zone.zone_id) > 1
                    ):
                        violation = "LANE_CHANGE"
                        self._log_violation(
                            track_id, violation,
                            current_zone, frame_number, obj["label"]
                        )

                # Update zone tracking
                self.vehicle_zones[track_id] = current_zone.zone_id
                self.zone_history[track_id].append(current_zone.zone_id)

            if violation:
                self.active_violations[track_id] = violation

            results.append({
                **obj,
                "violation": violation,
                "zone": current_zone.label if current_zone else "unknown",
            })

        return results

    def _log_violation(
        self,
        track_id: int,
        violation_type: str,
        zone: LaneZone,
        frame_number: int,
        label: str,
    ) -> None:
        """Record a violation event."""
        self.violations.append({
            "track_id": track_id,
            "violation_type": violation_type,
            "description": VIOLATION_TYPES[violation_type],
            "zone": zone.label,
            "frame": frame_number,
            "vehicle_type": label,
        })
        logger.warning(
            f"VIOLATION | ID={track_id} | "
            f"type={violation_type} | "
            f"zone={zone.label} | "
            f"frame={frame_number}"
        )

    def get_summary(self) -> dict:
        """Return violation summary."""
        if not self.violations:
            return {"total_violations": 0, "by_type": {}}

        by_type = defaultdict(int)
        for v in self.violations:
            by_type[v["violation_type"]] += 1

        return {
            "total_violations": len(self.violations),
            "by_type": dict(by_type),
            "violations": self.violations,
        }