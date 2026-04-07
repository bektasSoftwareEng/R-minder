import sqlite3
import os
from pathlib import Path


_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "rminder.db"


def get_connection() -> sqlite3.Connection:
    """Her çağrıda yeni bir bağlantı döner. Row factory ile dict-like erişim sağlar."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize() -> None:
    """Veritabanı dosyası ve tabloları yoksa oluşturur."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        _create_tables(conn)
        _seed_default_settings(conn)


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS recurrence_rules (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_type       TEXT NOT NULL,
            interval        INTEGER DEFAULT 1,
            day_of_week     TEXT,
            day_of_month    INTEGER,
            month_of_year   INTEGER,
            end_date        DATE,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            description     TEXT,
            due_date        DATE NOT NULL,
            due_time        TIME,
            is_completed    BOOLEAN DEFAULT 0,
            completed_at    DATETIME,
            recurrence_id   INTEGER REFERENCES recurrence_rules(id) ON DELETE SET NULL,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS task_exceptions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            recurrence_id    INTEGER NOT NULL REFERENCES recurrence_rules(id) ON DELETE CASCADE,
            original_date    DATE NOT NULL,
            modified_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
            is_deleted       BOOLEAN DEFAULT 0,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key     TEXT PRIMARY KEY,
            value   TEXT
        );
    """)


def _seed_default_settings(conn: sqlite3.Connection) -> None:
    defaults = [
        ("widget_x", "40"),
        ("widget_y", "40"),
        ("widget_width", "320"),
        ("widget_height", "520"),
        ("notification_lead_minutes", "15"),
        ("theme", "dark"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        defaults,
    )
