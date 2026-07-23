"""Generic database access utilities for PostgreSQL.

Provides a shared connection pool and thin wrappers for
common SQL operations (SELECT, INSERT, UPDATE, DELETE).
"""

import os
from contextlib import contextmanager

from psycopg2 import pool
from psycopg2.extras import RealDictCursor

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        dsn = os.environ.get("DATABASE_URL")
        if not dsn:
            raise RuntimeError(
                "DATABASE_URL environment variable not set. "
                "Create a .env file with DATABASE_URL=postgresql://... "
                "or set it via Streamlit Community Cloud secrets."
            )
        _pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=dsn,
        )
    return _pool


@contextmanager
def get_db():
    p = _get_pool()
    conn = p.getconn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        p.putconn(conn)


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
