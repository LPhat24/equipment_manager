"""Borrow and return workflow — validation, atomic status transitions."""

from datetime import date

from database import equipment_repo, borrow_repo
from database.db import get_db


def borrow_equipment(
    equipment_id: int,
    borrower_name: str,
    borrower_phone: str,
    borrow_date: str,
    expected_return_date: str,
    notes: str = "",
    borrow_quantity: int = 1,
) -> int:
    if not borrower_name.strip():
        raise ValueError("Borrower name is required")
    if len(borrower_name.strip()) < 2:
        raise ValueError("Borrower name must be at least 2 characters")
    if not borrower_phone.strip():
        raise ValueError("Borrower phone is required")
    digits_only = borrower_phone.strip().replace("-", "").replace(" ", "")
    if len(digits_only) < 8 or not digits_only.isdigit():
        raise ValueError("Phone number must be at least 8 digits")
    if not borrow_date:
        raise ValueError("Borrow date is required")
    if not expected_return_date:
        raise ValueError("Expected return date is required")
    if borrow_quantity < 1:
        raise ValueError("Borrow quantity must be at least 1")

    equipment = equipment_repo.find_by_id(equipment_id)
    if not equipment:
        raise ValueError("Equipment not found")
    if equipment["status"] == "Maintenance":
        raise ValueError("Equipment is currently under maintenance")

    available = equipment_repo.get_available_quantity(equipment_id)
    if available <= 0:
        raise ValueError("No copies available to borrow")
    if borrow_quantity > available:
        raise ValueError(
            f"Requested {borrow_quantity} but only {available} available"
        )

    if expected_return_date < borrow_date:
        raise ValueError("Expected return date must be on or after borrow date")
    if (date.fromisoformat(expected_return_date) - date.fromisoformat(borrow_date)).days > 90:
        raise ValueError("Borrow duration cannot exceed 90 days")

    with get_db() as cur:
        cur.execute(
            """INSERT INTO borrow_history
               (equipment_id, borrower_name, borrower_phone, borrow_quantity,
                borrow_date, expected_return_date, notes, asset_code, equipment_name)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (
                equipment_id,
                borrower_name.strip(),
                borrower_phone.strip(),
                borrow_quantity,
                borrow_date,
                expected_return_date,
                notes.strip(),
                equipment["asset_code"],
                equipment["name"],
            ),
        )
        new_id = cur.fetchone()["id"]

        new_available = available - borrow_quantity
        new_status = "Available" if new_available > 0 else "Borrowed"
        cur.execute(
            "UPDATE equipment SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_status, equipment_id),
        )
        return new_id


def return_equipment(record_id: int) -> None:
    record = borrow_repo.find_by_id(record_id)
    if not record:
        raise ValueError("Borrow record not found")
    if record["actual_return_date"]:
        raise ValueError("Equipment has already been returned")

    today = date.today().isoformat()

    with get_db() as cur:
        cur.execute(
            "UPDATE borrow_history SET actual_return_date = %s WHERE id = %s",
            (today, record_id),
        )

        remaining = borrow_repo.count_active_borrows_for(cur, record["equipment_id"])
        new_status = "Available" if remaining == 0 else "Borrowed"
        cur.execute(
            "UPDATE equipment SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_status, record["equipment_id"]),
        )


def get_active_borrows() -> list[dict]:
    return borrow_repo.find_all_active()


def get_active_borrow_for(equipment_id: int) -> dict | None:
    return borrow_repo.find_active_by_equipment(equipment_id)


def get_active_borrows_for(equipment_id: int) -> list[dict]:
    return borrow_repo.find_all_active_by_equipment(equipment_id)


def borrow_multiple(
    equipment_ids: list[int],
    borrower_name: str,
    borrower_phone: str,
    borrow_date: str,
    expected_return_date: str,
    notes: str = "",
    borrow_quantity: int = 1,
) -> tuple[int, list[dict]]:
    borrowed = 0
    skipped = []
    for eid in equipment_ids:
        try:
            borrow_equipment(
                eid, borrower_name, borrower_phone,
                borrow_date, expected_return_date, notes, borrow_quantity,
            )
            borrowed += 1
        except ValueError as e:
            equipment = equipment_repo.find_by_id(eid)
            if equipment:
                skipped.append({
                    "asset_code": equipment["asset_code"],
                    "name": equipment["name"],
                    "reason": str(e),
                })
    return borrowed, skipped
