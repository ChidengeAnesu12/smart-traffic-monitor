"""
Database Handler
Manages all SQLite database operations for the
traffic monitoring system.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from database.models import ALL_TABLES

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """
    Handles all database read/write operations.
    Uses SQLite with WAL mode for better performance.
    """

    def __init__(self, config: dict):
        self.db_path = config["database"]["path"]
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn = self._connect()
        self._create_tables()

        logger.info(f"DatabaseHandler initialized | path={self.db_path}")

    def _connect(self) -> sqlite3.Connection:
        """Create and configure database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # return dicts instead of tuples
        conn.execute("PRAGMA journal_mode=WAL")  # better concurrency
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _create_tables(self) -> None:
        """Create all tables if they don't exist."""
        with self.conn:
            for create_sql in ALL_TABLES:
                self.conn.execute(create_sql)
        logger.info("Database tables ready.")

    # ─── SESSION OPERATIONS ───────────────────────────────────────

    def create_session(self, session_id: str, video_source: str) -> None:
        """Create a new processing session record."""
        sql = """
            INSERT OR IGNORE INTO sessions
            (session_id, video_source, started_at, status)
            VALUES (?, ?, ?, 'running')
        """
        with self.conn:
            self.conn.execute(sql, (
                session_id,
                video_source,
                datetime.now().isoformat(),
            ))
        logger.info(f"Session created: {session_id}")

    def update_session(self, session_id: str, summary: dict) -> None:
        """Update session with final analytics summary."""
        sql = """
            UPDATE sessions SET
                ended_at         = ?,
                total_frames     = ?,
                total_counted    = ?,
                avg_density      = ?,
                peak_density     = ?,
                total_violations = ?,
                status           = 'completed'
            WHERE session_id = ?
        """
        with self.conn:
            self.conn.execute(sql, (
                datetime.now().isoformat(),
                summary.get("total_frames", 0),
                summary.get("total_vehicles_counted", 0),
                summary.get("avg_density", 0.0),
                summary.get("peak_density", 0.0),
                summary.get("total_violations", 0),
                session_id,
            ))
        logger.info(f"Session updated: {session_id}")

    # ─── VEHICLE OPERATIONS ───────────────────────────────────────

    def insert_vehicles(
        self, session_id: str, vehicle_records: Dict[int, dict]
    ) -> None:
        """Insert all vehicle records for a session."""
        sql = """
            INSERT INTO vehicles
            (session_id, track_id, label, first_frame, last_frame,
             avg_speed_kmh, max_speed_kmh, zone, violation, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = []
        for record in vehicle_records.values():
            rows.append((
                session_id,
                record["track_id"],
                record["label"],
                record["first_frame"],
                record["last_frame"],
                record.get("avg_speed"),
                record.get("max_speed"),
                record.get("zone"),
                record.get("violation"),
                datetime.now().isoformat(),
            ))

        with self.conn:
            self.conn.executemany(sql, rows)
        logger.info(f"Inserted {len(rows)} vehicle records.")

    # ─── FRAME RECORD OPERATIONS ─────────────────────────────────

    def insert_frame_records(
        self, session_id: str, frame_records: List[dict]
    ) -> None:
        """Bulk insert frame-level analytics records."""
        sql = """
            INSERT INTO frame_records
            (session_id, frame_number, vehicle_count,
             density_score, density_level, total_counted, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        rows = [
            (
                session_id,
                r["frame"],
                r["vehicle_count"],
                r["density_score"],
                r["density_level"],
                r["total_counted"],
                now,
            )
            for r in frame_records
        ]

        with self.conn:
            self.conn.executemany(sql, rows)
        logger.info(f"Inserted {len(rows)} frame records.")

    # ─── VIOLATION OPERATIONS ─────────────────────────────────────

    def insert_violations(
        self, session_id: str, violations: List[dict]
    ) -> None:
        """Insert violation events."""
        if not violations:
            return

        sql = """
            INSERT INTO violations
            (session_id, track_id, vehicle_type, violation_type,
             description, zone, frame_number, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        rows = [
            (
                session_id,
                v["track_id"],
                v["vehicle_type"],
                v["violation_type"],
                v["description"],
                v["zone"],
                v["frame"],
                now,
            )
            for v in violations
        ]

        with self.conn:
            self.conn.executemany(sql, rows)
        logger.info(f"Inserted {len(rows)} violation records.")

    # ─── QUERY OPERATIONS ─────────────────────────────────────────

    def get_all_sessions(self) -> List[dict]:
        """Return all sessions ordered by most recent."""
        sql = """
            SELECT * FROM sessions
            ORDER BY started_at DESC
        """
        cursor = self.conn.execute(sql)
        return [dict(row) for row in cursor.fetchall()]

    def get_session_summary(self, session_id: str) -> Optional[dict]:
        """Return summary for a specific session."""
        sql = "SELECT * FROM sessions WHERE session_id = ?"
        cursor = self.conn.execute(sql, (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_frame_records(self, session_id: str) -> List[dict]:
        """Return all frame records for a session."""
        sql = """
            SELECT * FROM frame_records
            WHERE session_id = ?
            ORDER BY frame_number ASC
        """
        cursor = self.conn.execute(sql, (session_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_vehicles(self, session_id: str) -> List[dict]:
        """Return all vehicle records for a session."""
        sql = """
            SELECT * FROM vehicles
            WHERE session_id = ?
            ORDER BY track_id ASC
        """
        cursor = self.conn.execute(sql, (session_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_violations(self, session_id: str) -> List[dict]:
        """Return all violations for a session."""
        sql = """
            SELECT * FROM violations
            WHERE session_id = ?
            ORDER BY frame_number ASC
        """
        cursor = self.conn.execute(sql, (session_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_recent_density(
        self, session_id: str, limit: int = 100
    ) -> List[dict]:
        """Return recent frame density records for live dashboard."""
        sql = """
            SELECT frame_number, vehicle_count, density_score, density_level
            FROM frame_records
            WHERE session_id = ?
            ORDER BY frame_number DESC
            LIMIT ?
        """
        cursor = self.conn.execute(sql, (session_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
        logger.info("Database connection closed.")