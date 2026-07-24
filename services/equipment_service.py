"""Equipment business logic — validation, CRUD, and filtering."""

from database import equipment_repo, borrow_repo

VALID_STATUSES = {"Available", "Borrowed", "Maintenance"}
VALID_CONDITIONS = {"Good", "Fair", "Poor", "Damaged"}


def get_all_equipment(
    categories: list[str] | None = None,
    statuses: list[str] | None = None,
    locations: list[str] | None = None,
    search: str | None = None,
) -> list[dict]:
    return equipment_repo.find_filtered_with_availability(
        categories=categories, statuses=statuses, locations=locations, search=search
    )


def get_equipment(equipment_id: int) -> dict:
    item = equipment_repo.find_by_id(equipment_id)
    if not item:
        raise ValueError("Equipment not found")
    item["available_quantity"] = equipment_repo.get_available_quantity(equipment_id)
    return item


def add_equipment(data: dict) -> int:
    if not data.get("asset_code", "").strip():
        raise ValueError("Asset code is required")
    if not data.get("name", "").strip():
        raise ValueError("Equipment name is required")

    if data.get("status") not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {data.get('status')}")
    if data.get("condition") not in VALID_CONDITIONS:
        raise ValueError(f"Invalid condition: {data.get('condition')}")

    try:
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        raise ValueError("Quantity must be a valid number")
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")

    existing = equipment_repo.find_by_asset_code(data["asset_code"].strip())
    if existing:
        raise ValueError(f"Asset code '{data['asset_code']}' already exists")

    clean_data = {
        "asset_code": data["asset_code"].strip(),
        "name": data["name"].strip(),
        "category": data.get("category", "").strip(),
        "location": data.get("location", "").strip(),
        "status": data["status"],
        "condition": data["condition"],
        "quantity": quantity,
        "notes": data.get("notes", "").strip(),
    }
    return equipment_repo.insert_equipment(clean_data)


def update_equipment(equipment_id: int, data: dict) -> None:
    existing = equipment_repo.find_by_id(equipment_id)
    if not existing:
        raise ValueError("Equipment not found")

    if not data.get("name", "").strip():
        raise ValueError("Equipment name is required")

    if data.get("status") not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {data.get('status')}")
    if data.get("condition") not in VALID_CONDITIONS:
        raise ValueError(f"Invalid condition: {data.get('condition')}")

    try:
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        raise ValueError("Quantity must be a valid number")
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")

    available = equipment_repo.get_available_quantity(equipment_id)
    active_borrows = existing["quantity"] - available
    if quantity < active_borrows:
        raise ValueError(
            f"Cannot reduce quantity below {active_borrows} — "
            f"{active_borrows} copy(ies) currently borrowed"
        )

    new_asset_code = data.get("asset_code", "").strip()
    if new_asset_code and new_asset_code != existing["asset_code"]:
        duplicate = equipment_repo.find_by_asset_code(new_asset_code)
        if duplicate:
            raise ValueError(f"Asset code '{new_asset_code}' already exists")

    clean_data = {
        "asset_code": new_asset_code or existing["asset_code"],
        "name": data["name"].strip(),
        "category": data.get("category", "").strip(),
        "location": data.get("location", "").strip(),
        "status": data["status"],
        "condition": data["condition"],
        "quantity": quantity,
        "notes": data.get("notes", "").strip(),
    }
    equipment_repo.update_equipment(equipment_id, clean_data)


def delete_equipment(equipment_id: int) -> None:
    existing = equipment_repo.find_by_id(equipment_id)
    if not existing:
        raise ValueError("Equipment not found")

    available = equipment_repo.get_available_quantity(equipment_id)
    if available < existing["quantity"]:
        raise ValueError("Cannot delete — this equipment has active borrows")

    equipment_repo.delete_equipment(equipment_id)


def delete_multiple(equipment_ids: list[int]) -> tuple[int, list[dict]]:
    deleted = 0
    skipped = []
    for eid in equipment_ids:
        existing = equipment_repo.find_by_id(eid)
        if not existing:
            continue
        available = equipment_repo.get_available_quantity(eid)
        if available < existing["quantity"]:
            skipped.append({"asset_code": existing["asset_code"], "name": existing["name"]})
        else:
            equipment_repo.delete_equipment(eid)
            deleted += 1
    return deleted, skipped


def scan_csv_rows(rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Pre-scan CSV rows for duplicates and validation errors before import.

    Returns:
        clean_rows: list of {row, index} for rows with no conflicts
        duplicates: list of {row, index, existing} for rows with name duplicates
        errors: list of {row, index, reason} for rows with invalid data
    """
    clean_rows = []
    duplicates = []
    errors = []
    seen_codes = set()

    for i, row in enumerate(rows, 1):
        name = row.get("name", "").strip()
        asset_code = row.get("asset_code", "").strip()

        if not name:
            errors.append({
                "row": row,
                "index": i,
                "reason": "Missing equipment name",
            })
            continue

        if not asset_code:
            errors.append({
                "row": row,
                "index": i,
                "reason": "Missing asset code",
            })
            continue

        status = row.get("status", "").strip()
        if status not in VALID_STATUSES:
            errors.append({
                "row": row,
                "index": i,
                "reason": f"Invalid status: '{status}' (must be Available, Borrowed, or Maintenance)",
            })
            continue

        condition = row.get("condition", "").strip()
        if condition not in VALID_CONDITIONS:
            errors.append({
                "row": row,
                "index": i,
                "reason": f"Invalid condition: '{condition}' (must be Good, Fair, Poor, or Damaged)",
            })
            continue

        try:
            quantity = int(row.get("quantity", 1))
            if quantity < 1:
                errors.append({
                    "row": row,
                    "index": i,
                    "reason": f"Invalid quantity: '{row.get('quantity', '')}' (must be at least 1)",
                })
                continue
        except (ValueError, TypeError):
            errors.append({
                "row": row,
                "index": i,
                "reason": f"Invalid quantity: '{row.get('quantity', '')}' (must be a valid number)",
            })
            continue

        if asset_code in seen_codes:
            errors.append({
                "row": row,
                "index": i,
                "reason": f"Duplicate asset code '{asset_code}' within the CSV file",
            })
            continue

        existing_by_name = equipment_repo.find_by_name(name)
        if existing_by_name:
            duplicates.append({
                "row": row,
                "index": i,
                "existing": existing_by_name,
            })
        else:
            existing_by_code = equipment_repo.find_by_asset_code(asset_code)
            if existing_by_code:
                errors.append({
                    "row": row,
                    "index": i,
                    "reason": f"Asset code '{asset_code}' already exists",
                })
            else:
                clean_rows.append({"row": row, "index": i})
                seen_codes.add(asset_code)

    return clean_rows, duplicates, errors


def import_csv_rows(
    rows: list[dict],
    duplicate_ids: list[int] | None = None,
) -> tuple[int, int, list[str]]:
    """Import CSV rows with duplicate handling.

    Args:
        rows: list of {row, index, action} dicts
        duplicate_ids: list of equipment IDs to increase quantity for

    Returns:
        (inserted, increased, errors)
    """
    inserted = 0
    increased = 0
    errors = []

    duplicate_ids = duplicate_ids or []

    for item in rows:
        row = item["row"]
        index = item["index"]
        action = item.get("action", "add")

        name = row.get("name", "").strip()
        asset_code = row.get("asset_code", "").strip()

        if not name:
            errors.append(f"Row {index}: Equipment name is required")
            continue

        if action == "increase":
            existing = equipment_repo.find_by_id(item.get("existing_id"))
            if not existing:
                errors.append(f"Row {index}: Equipment not found")
                continue

            try:
                qty = int(row.get("quantity", 1))
            except (ValueError, TypeError):
                errors.append(f"Row {index}: Quantity must be a valid number")
                continue

            if qty < 1:
                errors.append(f"Row {index}: Quantity must be at least 1")
                continue

            equipment_repo.increase_quantity(existing["id"], qty)
            increased += 1
        else:
            if not asset_code:
                errors.append(f"Row {index}: Asset code is required")
                continue

            if row.get("status") not in VALID_STATUSES:
                errors.append(f"Row {index}: Invalid status: {row.get('status')}")
                continue
            if row.get("condition") not in VALID_CONDITIONS:
                errors.append(f"Row {index}: Invalid condition: {row.get('condition')}")
                continue

            try:
                quantity = int(row.get("quantity", 1))
            except (ValueError, TypeError):
                errors.append(f"Row {index}: Quantity must be a valid number")
                continue
            if quantity < 1:
                errors.append(f"Row {index}: Quantity must be at least 1")
                continue

            existing_code = equipment_repo.find_by_asset_code(asset_code)
            if existing_code:
                errors.append(f"Row {index}: Asset code '{asset_code}' already exists")
                continue

            clean_data = {
                "asset_code": asset_code,
                "name": name,
                "category": row.get("category", "").strip(),
                "location": row.get("location", "").strip(),
                "status": row["status"],
                "condition": row["condition"],
                "quantity": quantity,
                "notes": row.get("notes", "").strip(),
            }
            equipment_repo.insert_equipment(clean_data)
            inserted += 1

    return inserted, increased, errors


def get_categories() -> list[str]:
    return equipment_repo.find_distinct_categories()


def get_locations() -> list[str]:
    return equipment_repo.find_distinct_locations()


SAMPLE_EQUIPMENT = [
    {"asset_code": "EQ-001", "name": "Oscilloscope", "category": "Test Equipment", "location": "Lab A, Bench 1", "status": "Available", "condition": "Good", "quantity": 2, "notes": "Keysight DSOX1202G"},
    {"asset_code": "EQ-002", "name": "Digital Multimeter", "category": "Measurement", "location": "Lab A, Bench 2", "status": "Available", "condition": "Good", "quantity": 4, "notes": "Fluke 87V"},
    {"asset_code": "EQ-003", "name": "Function Generator", "category": "Test Equipment", "location": "Lab A, Bench 1", "status": "Available", "condition": "Good", "quantity": 1, "notes": "Siglent SDG1032X"},
    {"asset_code": "EQ-004", "name": "DC Power Supply", "category": "Power", "location": "Lab B, Bench 1", "status": "Available", "condition": "Fair", "quantity": 3, "notes": "Rigol DP832"},
    {"asset_code": "EQ-005", "name": "Soldering Station", "category": "Tools", "location": "Lab B, Bench 3", "status": "Available", "condition": "Good", "quantity": 2, "notes": "Hakko FX-888D"},
    {"asset_code": "EQ-006", "name": "LCR Meter", "category": "Measurement", "location": "Lab A, Bench 3", "status": "Maintenance", "condition": "Poor", "quantity": 1, "notes": "Needs calibration"},
    {"asset_code": "EQ-007", "name": "Logic Analyzer", "category": "Test Equipment", "location": "Lab C, Bench 1", "status": "Available", "condition": "Good", "quantity": 1, "notes": "Saleae Logic Pro 16"},
    {"asset_code": "EQ-008", "name": "Breadboard Kit", "category": "Components", "location": "Lab A, Storage", "status": "Available", "condition": "Good", "quantity": 10, "notes": "Includes jumper wires"},
]


def reset_all_data() -> None:
    borrow_repo.delete_all()
    equipment_repo.delete_all()


def load_sample_data() -> tuple[int, list[str]]:
    inserted = 0
    errors = []
    for i, item in enumerate(SAMPLE_EQUIPMENT, 1):
        try:
            add_equipment(item)
            inserted += 1
        except ValueError as e:
            errors.append(f"Row {i} ({item['asset_code']}): {e}")
    return inserted, errors
