"""Generic database access utilities for PostgreSQL.

Provides connection context management and thin wrappers for
common SQL operations (SELECT, INSERT, UPDATE, DELETE).
"""

from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from database.schema import get_connection


@contextmanager
def get_db():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    with get_db() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    with get_db() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def insert(table: str, data: dict) -> int:
    columns = ", ".join(data.keys())
    placeholders = ", ".join("%s" for _ in data)
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
    with get_db() as cur:
        cur.execute(sql, tuple(data.values()))
        return cur.fetchone()["id"]


def update(sql: str, params: tuple = ()) -> int:
    with get_db() as cur:
        cur.execute(sql, params)
        return cur.rowcount
