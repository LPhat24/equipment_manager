"""Database schema definition and connection management for PostgreSQL."""

import os

import psycopg2
from psycopg2.extras import RealDictCursor

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS equipment (
    id              SERIAL PRIMARY KEY,
    asset_code      TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    category        TEXT DEFAULT '',
    location        TEXT DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'Available',
    condition       TEXT DEFAULT 'Good',
    quantity        INTEGER NOT NULL DEFAULT 1,
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borrow_history (
    id                  SERIAL PRIMARY KEY,
    equipment_id        INTEGER NOT NULL,
    borrower_name       TEXT NOT NULL,
    borrower_phone      TEXT DEFAULT '',
    borrow_quantity     INTEGER NOT NULL DEFAULT 1,
    borrow_date         TEXT NOT NULL,
    expected_return_date TEXT NOT NULL,
    actual_return_date  TEXT DEFAULT NULL,
    notes               TEXT DEFAULT '',
    asset_code          TEXT DEFAULT '',
    equipment_name      TEXT DEFAULT '',
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_equipment_status   ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_category ON equipment(category);
CREATE INDEX IF NOT EXISTS idx_equipment_location ON equipment(location);

CREATE INDEX IF NOT EXISTS idx_borrow_equipment_id ON borrow_history(equipment_id);
CREATE INDEX IF NOT EXISTS idx_borrow_active       ON borrow_history(actual_return_date);

ALTER TABLE borrow_history ADD COLUMN IF NOT EXISTS borrow_quantity INTEGER NOT NULL DEFAULT 1;
ALTER TABLE borrow_history ADD COLUMN IF NOT EXISTS original_status TEXT;
"""


def get_connection():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError(
            "DATABASE_URL environment variable not set. "
            "Create a .env file with DATABASE_URL=postgresql://... "
            "or set it via Streamlit Community Cloud secrets."
        )
    conn = psycopg2.connect(dsn)
    return conn


def _execute_sql(conn, script: str):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for statement in script.split(";"):
            stmt = statement.strip()
            if stmt:
                cur.execute(stmt + ";")


def init_db():
    conn = get_connection()
    try:
        _execute_sql(conn, _CREATE_TABLES)
        conn.commit()
    finally:
        conn.close()
