"""
Database Models
Defines SQLite schema for the traffic monitoring system.
Uses raw SQL for simplicity and transparency.
"""

CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL UNIQUE,
    video_source    TEXT NOT NULL,
    started_at      TEXT NOT NULL,
    ended_at        TEXT,
    total_frames    INTEGER DEFAULT 0,
    total_counted   INTEGER DEFAULT 0,
    avg_density     REAL DEFAULT 0.0,
    peak_density    REAL DEFAULT 0.0,
    avg_speed_kmh   REAL,
    max_speed_kmh   REAL,
    total_violations INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'running'
);
"""

CREATE_VEHICLES_TABLE = """
CREATE TABLE IF NOT EXISTS vehicles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    track_id        INTEGER NOT NULL,
    label           TEXT NOT NULL,
    first_frame     INTEGER NOT NULL,
    last_frame      INTEGER NOT NULL,
    avg_speed_kmh   REAL,
    max_speed_kmh   REAL,
    zone            TEXT,
    violation       TEXT,
    created_at      TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""

CREATE_FRAME_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS frame_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    frame_number    INTEGER NOT NULL,
    vehicle_count   INTEGER NOT NULL,
    density_score   REAL NOT NULL,
    density_level   TEXT NOT NULL,
    total_counted   INTEGER NOT NULL,
    recorded_at     TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""

CREATE_VIOLATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS violations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    track_id        INTEGER NOT NULL,
    vehicle_type    TEXT NOT NULL,
    violation_type  TEXT NOT NULL,
    description     TEXT NOT NULL,
    zone            TEXT NOT NULL,
    frame_number    INTEGER NOT NULL,
    recorded_at     TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""

ALL_TABLES = [
    CREATE_SESSIONS_TABLE,
    CREATE_VEHICLES_TABLE,
    CREATE_FRAME_RECORDS_TABLE,
    CREATE_VIOLATIONS_TABLE,
]