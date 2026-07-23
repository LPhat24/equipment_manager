"""One-time migration script: SQLite → PostgreSQL (Neon).

Reads data from the old local SQLite database and inserts it into
the Neon PostgreSQL database.

Usage:
    python scripts/migrate_sqlite_to_pg.py            # skip tables with existing data
    python scripts/migrate_sqlite_to_pg.py --force    # clear + re-import everything
"""

import os
import sqlite3
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

SQLITE_PATH = Path(__file__).resolve().parent.parent / "database" / "database.db"
FORCE = "--force" in sys.argv


def main():
    print("Connecting to SQLite...")
    if not SQLITE_PATH.exists():
        print(f"  SQLite database not found at {SQLITE_PATH}")
        return

    sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
    sqlite_conn.row_factory = sqlite3.Row

    equipment_rows = sqlite_conn.execute("SELECT * FROM equipment ORDER BY id").fetchall()
    borrow_rows = sqlite_conn.execute("SELECT * FROM borrow_history ORDER BY id").fetchall()
    print(f"  Found {len(equipment_rows)} equipment, {len(borrow_rows)} borrow records")

    print("Connecting to Neon PostgreSQL...")
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("  DATABASE_URL not set. Check your .env file.")
        return

    pg_conn = psycopg2.connect(dsn)
    pg_conn.autocommit = False

    try:
        with pg_conn.cursor(cursor_factory=RealDictCursor) as cur:
            # --- Equipment ---
            cur.execute("SELECT COUNT(*) AS c FROM equipment")
            existing = cur.fetchone()["c"]

            if existing > 0 and not FORCE:
                print(f"  Equipment table already has {existing} rows — skipping (use --force to overwrite)")
            else:
                if existing > 0:
                    print(f"  Equipment table has {existing} rows — clearing (--force)")
                    cur.execute("DELETE FROM borrow_history")
                    cur.execute("DELETE FROM equipment")

                print(f"  Migrating equipment... ", end="")
                for row in equipment_rows:
                    cur.execute(
                        """INSERT INTO equipment
                           (id, asset_code, name, category, location, status,
                            condition, quantity, notes, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            row["id"], row["asset_code"], row["name"],
                            row["category"], row["location"], row["status"],
                            row["condition"], row["quantity"], row["notes"],
                            row["created_at"], row["updated_at"],
                        ),
                    )
                print(f"{len(equipment_rows)} rows inserted")

                max_id = max(r["id"] for r in equipment_rows) if equipment_rows else 0
                cur.execute("SELECT setval(pg_get_serial_sequence('equipment', 'id'), %s)", (max_id,))

            # --- Borrow history ---
            cur.execute("SELECT COUNT(*) AS c FROM borrow_history")
            existing = cur.fetchone()["c"]

            if existing > 0 and not FORCE:
                print(f"  borrow_history table already has {existing} rows — skipping (use --force to overwrite)")
            else:
                if existing > 0:
                    print(f"  borrow_history table has {existing} rows — clearing (--force)")
                    cur.execute("DELETE FROM borrow_history")

                print(f"  Migrating borrow_history... ", end="")
                for row in borrow_rows:
                    cur.execute(
                        """INSERT INTO borrow_history
                           (id, equipment_id, borrower_name, borrower_phone,
                            borrow_date, expected_return_date, actual_return_date,
                            notes, asset_code, equipment_name, created_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            row["id"], row["equipment_id"], row["borrower_name"],
                            row["borrower_phone"], row["borrow_date"],
                            row["expected_return_date"], row["actual_return_date"],
                            row["notes"], row["asset_code"],
                            row["equipment_name"], row["created_at"],
                        ),
                    )
                print(f"{len(borrow_rows)} rows inserted")

                if borrow_rows:
                    max_id = max(r["id"] for r in borrow_rows)
                    cur.execute("SELECT setval(pg_get_serial_sequence('borrow_history', 'id'), %s)", (max_id,))

        pg_conn.commit()
        print("Migration complete!")

    except Exception as e:
        pg_conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        pg_conn.close()
        sqlite_conn.close()


if __name__ == "__main__":
    main()
