"""Equipment table data access operations."""

from database.db import fetch_all, fetch_one, insert, update


def find_all() -> list[dict]:
    return fetch_all("SELECT * FROM equipment ORDER BY asset_code")


def find_by_id(equipment_id: int) -> dict | None:
    return fetch_one("SELECT * FROM equipment WHERE id = %s", (equipment_id,))


def find_by_asset_code(asset_code: str) -> dict | None:
    return fetch_one("SELECT * FROM equipment WHERE asset_code = %s", (asset_code,))


def insert_equipment(data: dict) -> int:
    return insert("equipment", data)


def update_equipment(equipment_id: int, data: dict) -> int:
    set_clause = ", ".join(f"{key} = %s" for key in data)
    sql = f"UPDATE equipment SET {set_clause} WHERE id = %s"
    return update(sql, (*data.values(), equipment_id))


def delete_equipment(equipment_id: int) -> int:
    return update("DELETE FROM equipment WHERE id = %s", (equipment_id,))


def find_distinct_categories() -> list[str]:
    rows = fetch_all(
        "SELECT DISTINCT category FROM equipment WHERE category != '' ORDER BY category"
    )
    return [row["category"] for row in rows]


def find_distinct_locations() -> list[str]:
    rows = fetch_all(
        "SELECT DISTINCT location FROM equipment WHERE location != '' ORDER BY location"
    )
    return [row["location"] for row in rows]


def delete_all() -> int:
    return update("DELETE FROM equipment")


def get_available_quantity(equipment_id: int) -> int:
    row = fetch_one(
        """SELECT e.quantity - COALESCE(SUM(bh.borrow_quantity), 0) AS available
           FROM equipment e
           LEFT JOIN borrow_history bh ON bh.equipment_id = e.id AND bh.actual_return_date IS NULL
           WHERE e.id = %s
           GROUP BY e.quantity""",
        (equipment_id,),
    )
    return row["available"] if row else 0


def get_available_quantities_bulk() -> dict[int, int]:
    rows = fetch_all(
        """SELECT e.id,
                  e.quantity - COALESCE(SUM(bh.borrow_quantity), 0) AS available
           FROM equipment e
           LEFT JOIN borrow_history bh ON bh.equipment_id = e.id AND bh.actual_return_date IS NULL
           GROUP BY e.id, e.quantity"""
    )
    return {row["id"]: row["available"] for row in rows}


def find_filtered(
    categories: list[str] | None = None,
    statuses: list[str] | None = None,
    locations: list[str] | None = None,
    search: str | None = None,
) -> list[dict]:
    conditions = []
    params: list = []

    if categories:
        placeholders = ", ".join(["%s"] * len(categories))
        conditions.append(f"category IN ({placeholders})")
        params.extend(categories)
    if statuses:
        placeholders = ", ".join(["%s"] * len(statuses))
        conditions.append(f"status IN ({placeholders})")
        params.extend(statuses)
    if locations:
        placeholders = ", ".join(["%s"] * len(locations))
        conditions.append(f"location IN ({placeholders})")
        params.extend(locations)
    if search:
        conditions.append("(name LIKE %s OR asset_code LIKE %s OR notes LIKE %s)")
        term = f"%{search}%"
        params.extend([term, term, term])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM equipment {where} ORDER BY asset_code"
    return fetch_all(sql, tuple(params))
