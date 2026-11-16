"""Small local SQLite history store for demonstration records."""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from .models import FEATURES

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "orbita.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            crew_id TEXT NOT NULL,
            scenario TEXT NOT NULL,
            sleep_hours REAL, activity_index REAL, stress_index REAL,
            radiation_index REAL, hr_deviation_index REAL,
            data_label TEXT NOT NULL DEFAULT 'synthetic_demo'
        )
        """)

def save_reading(crew_id: str, scenario: str, values: dict):
    keys = ", ".join(FEATURES)
    marks = ", ".join(["?"] * len(FEATURES))
    with connect() as con:
        con.execute(
            f"INSERT INTO readings (created_at, crew_id, scenario, {keys}, data_label) "
            f"VALUES (?, ?, ?, {marks}, 'synthetic_demo')",
            [datetime.now(timezone.utc).isoformat(), crew_id, scenario] +
            [float(values[k]) for k in FEATURES]
        )

def latest_readings(limit: int = 100):
    with connect() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
