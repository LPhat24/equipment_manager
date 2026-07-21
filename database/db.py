"""Generic database access utilities.

Provides connection context management and thin wrappers for
common SQL operations (SELECT, INSERT, UPDATE, DELETE).
"""

import sqlite3
from contextlib import contextmanager

from database.schema import get_connection, init_db


@contextmanager
def get_db():
    """Context manager that yields a connection with auto-commit, auto-rollback, and auto-close."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    """Execute a SELECT query and return a single row, or None if no match."""
    with get_db() as conn:
        return conn.execute(sql, params).fetchone()


def fetch_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Execute a SELECT query and return all matching rows."""
    with get_db() as conn:
        return conn.execute(sql, params).fetchall()


def insert(table: str, data: dict) -> int:
    """Insert a row into the given table and return the new row ID."""
    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    with get_db() as conn:
        cursor = conn.execute(sql, tuple(data.values()))
        return cursor.lastrowid


def update(sql: str, params: tuple = ()) -> int:
    """Execute an UPDATE or DELETE statement and return the number of affected rows."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        return cursor.rowcount
