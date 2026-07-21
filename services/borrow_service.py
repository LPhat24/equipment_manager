"""Borrow and return workflow — validation, atomic status transitions."""

import sqlite3
from datetime import date

from database import equipment_repo, borrow_repo
from database.db import get_db


def borrow_equipment(
    equipment_id: int,
    borrower_name: str,
    borrow_date: str,
    expected_return_date: str,
    notes: str = "",
) -> int:
    if not borrower_name.strip():
        raise ValueError("Borrower name is required")
    if not borrow_date:
        raise ValueError("Borrow date is required")
    if not expected_return_date:
        raise ValueError("Expected return date is required")

    equipment = equipment_repo.find_by_id(equipment_id)
    if not equipment:
        raise ValueError("Equipment not found")
    if equipment["status"] != "Available":
        raise ValueError(
            f"Equipment is not available — current status: {equipment['status']}"
        )

    active = borrow_repo.find_active_by_equipment(equipment_id)
    if active:
        raise ValueError("Equipment already has an active borrow record")

    if expected_return_date < borrow_date:
        raise ValueError("Expected return date must be on or after borrow date")

    record_data = {
        "equipment_id": equipment_id,
        "borrower_name": borrower_name.strip(),
        "borrow_date": borrow_date,
        "expected_return_date": expected_return_date,
        "notes": notes.strip(),
        "asset_code": equipment["asset_code"],
        "equipment_name": equipment["name"],
    }

    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO borrow_history
               (equipment_id, borrower_name, borrow_date, expected_return_date, notes,
                asset_code, equipment_name)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record_data["equipment_id"],
                record_data["borrower_name"],
                record_data["borrow_date"],
                record_data["expected_return_date"],
                record_data["notes"],
                record_data["asset_code"],
                record_data["equipment_name"],
            ),
        )
        conn.execute(
            "UPDATE equipment SET status = 'Borrowed', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (equipment_id,),
        )
        return cursor.lastrowid


def return_equipment(record_id: int) -> None:
    record = borrow_repo.find_by_id(record_id)
    if not record:
        raise ValueError("Borrow record not found")
    if record["actual_return_date"]:
        raise ValueError("Equipment has already been returned")

    today = date.today().isoformat()

    with get_db() as conn:
        conn.execute(
            "UPDATE borrow_history SET actual_return_date = ? WHERE id = ?",
            (today, record_id),
        )
        conn.execute(
            "UPDATE equipment SET status = 'Available', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (record["equipment_id"],),
        )


def get_active_borrows() -> list[sqlite3.Row]:
    return borrow_repo.find_all_active()


def get_active_borrow_for(equipment_id: int) -> sqlite3.Row | None:
    return borrow_repo.find_active_by_equipment(equipment_id)
