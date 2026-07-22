"""Database schema definition and connection management.

Handles table creation, index creation, migration, and SQLite connection configuration.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS equipment (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_code      TEXT    UNIQUE NOT NULL,
    name            TEXT    NOT NULL,
    category        TEXT    DEFAULT '',
    location        TEXT    DEFAULT '',
    status          TEXT    NOT NULL DEFAULT 'Available',
    condition       TEXT    DEFAULT 'Good',
    quantity        INTEGER NOT NULL DEFAULT 1,
    notes           TEXT    DEFAULT '',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borrow_history (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id        INTEGER NOT NULL,
    borrower_name       TEXT    NOT NULL,
    borrower_phone      TEXT    DEFAULT '',
    borrow_date         TEXT    NOT NULL,
    expected_return_date TEXT   NOT NULL,
    actual_return_date  TEXT    DEFAULT NULL,
    notes               TEXT    DEFAULT '',
    asset_code          TEXT    DEFAULT '',
    equipment_name      TEXT    DEFAULT '',
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_equipment_status   ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_category ON equipment(category);
CREATE INDEX IF NOT EXISTS idx_equipment_location ON equipment(location);

CREATE INDEX IF NOT EXISTS idx_borrow_equipment_id ON borrow_history(equipment_id);
CREATE INDEX IF NOT EXISTS idx_borrow_active       ON borrow_history(actual_return_date);
"""

_MIGRATE_BORROW_HISTORY = """
CREATE TABLE IF NOT EXISTS _borrow_history_new (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id        INTEGER NOT NULL,
    borrower_name       TEXT    NOT NULL,
    borrower_phone      TEXT    DEFAULT '',
    borrow_date         TEXT    NOT NULL,
    expected_return_date TEXT   NOT NULL,
    actual_return_date  TEXT    DEFAULT NULL,
    notes               TEXT    DEFAULT '',
    asset_code          TEXT    DEFAULT '',
    equipment_name      TEXT    DEFAULT '',
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO _borrow_history_new
    (id, equipment_id, borrower_name, borrow_date, expected_return_date,
     actual_return_date, notes, asset_code, equipment_name, created_at)
SELECT id, equipment_id, borrower_name, borrow_date, expected_return_date,
       actual_return_date, notes, asset_code, equipment_name, created_at
FROM borrow_history;

DROP TABLE borrow_history;
ALTER TABLE _borrow_history_new RENAME TO borrow_history;
"""


def _needs_migration(conn: sqlite3.Connection) -> bool:
    """Check if borrow_history table needs migration (missing borrower_phone column)."""
    cursor = conn.execute("PRAGMA table_info(borrow_history)")
    columns = [row[1] for row in cursor.fetchall()]
    return "borrower_phone" not in columns


def get_connection() -> sqlite3.Connection:
    """Create a new SQLite connection with Row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables, indexes, and run any necessary schema migrations."""
    conn = get_connection()
    try:
        conn.executescript(_CREATE_TABLES)
        if _needs_migration(conn):
            conn.executescript(_MIGRATE_BORROW_HISTORY)
            conn.executescript(_CREATE_TABLES)
        conn.commit()
    finally:
        conn.close()
