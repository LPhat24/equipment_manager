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


def find_filtered(
    category: str | None = None,
    status: str | None = None,
    location: str | None = None,
    search: str | None = None,
) -> list[dict]:
    conditions = []
    params: list = []

    if category:
        conditions.append("category = %s")
        params.append(category)
    if status:
        conditions.append("status = %s")
        params.append(status)
    if location:
        conditions.append("location = %s")
        params.append(location)
    if search:
        conditions.append("(name LIKE %s OR asset_code LIKE %s OR notes LIKE %s)")
        term = f"%{search}%"
        params.extend([term, term, term])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM equipment {where} ORDER BY asset_code"
    return fetch_all(sql, tuple(params))
