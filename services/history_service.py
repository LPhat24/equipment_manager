"""History queries and statistics for dashboard and reporting."""

import sqlite3

from database import equipment_repo, borrow_repo


def get_equipment_history(equipment_id: int) -> list[sqlite3.Row]:
    equipment = equipment_repo.find_by_id(equipment_id)
    if not equipment:
        raise ValueError("Equipment not found")
    return borrow_repo.find_by_equipment(equipment_id)


def get_all_history() -> list[sqlite3.Row]:
    return borrow_repo.find_all()


def get_statistics() -> dict[str, int]:
    all_items = equipment_repo.find_all()
    total_quantity = sum(item["quantity"] for item in all_items)

    status_counts = {"Available": 0, "Borrowed": 0, "Maintenance": 0}
    for item in all_items:
        status = item["status"]
        if status in status_counts:
            status_counts[status] += 1

    return {
        "total_items": len(all_items),
        "total_quantity": total_quantity,
        "available": status_counts["Available"],
        "borrowed": status_counts["Borrowed"],
        "maintenance": status_counts["Maintenance"],
        "active_borrows": borrow_repo.count_active(),
    }
