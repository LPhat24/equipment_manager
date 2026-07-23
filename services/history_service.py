"""History queries and statistics for dashboard and reporting."""

from database import equipment_repo, borrow_repo


def get_equipment_history(equipment_id: int) -> list[dict]:
    equipment = equipment_repo.find_by_id(equipment_id)
    if not equipment:
        raise ValueError("Equipment not found")
    return borrow_repo.find_by_equipment(equipment_id)


def get_all_history() -> list[dict]:
    return borrow_repo.find_all()


def get_statistics() -> dict[str, int]:
    all_items = equipment_repo.find_all()
    total_quantity = sum(item["quantity"] for item in all_items)
    avail = equipment_repo.get_available_quantities_bulk()

    available_items = 0
    borrowed_items = 0
    maintenance_items = 0
    total_available_qty = 0

    for item in all_items:
        available_qty = avail.get(item["id"], item["quantity"])
        total_available_qty += available_qty
        if item["status"] == "Maintenance":
            maintenance_items += 1
        elif available_qty == 0:
            borrowed_items += 1
        else:
            available_items += 1

    return {
        "total_items": len(all_items),
        "total_quantity": total_quantity,
        "available": available_items,
        "borrowed": borrowed_items,
        "maintenance": maintenance_items,
        "total_available_qty": total_available_qty,
        "active_borrows": borrow_repo.count_active(),
    }
