"""
Query the database and print results.
Use this to verify data was saved correctly.
"""

import sys
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from database.db_handler import DatabaseHandler


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    db = DatabaseHandler(config)

    print("\n" + "=" * 50)
    print("ALL SESSIONS")
    print("=" * 50)
    sessions = db.get_all_sessions()
    for s in sessions:
        print(f"\nSession : {s['session_id']}")
        print(f"  Video         : {s['video_source']}")
        print(f"  Status        : {s['status']}")
        print(f"  Frames        : {s['total_frames']}")
        print(f"  Counted       : {s['total_counted']}")
        print(f"  Avg density   : {s['avg_density']}")
        print(f"  Violations    : {s['total_violations']}")
        print(f"  Started       : {s['started_at']}")
        print(f"  Ended         : {s['ended_at']}")

        # Vehicles for this session
        vehicles = db.get_vehicles(s["session_id"])
        print(f"\n  Vehicles tracked: {len(vehicles)}")
        for v in vehicles:
            speed = f"{v['avg_speed_kmh']} km/h" if v["avg_speed_kmh"] else "N/A"
            print(
                f"    ID={v['track_id']} | {v['label']} | "
                f"speed={speed} | zone={v['zone']}"
            )

    print("\n" + "=" * 50)
    db.close()


if __name__ == "__main__":
    main()