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
    return equipment_repo.find_filtered(
        categories=categories, statuses=statuses, locations=locations, search=search
    )


def get_equipment(equipment_id: int) -> dict:
    item = equipment_repo.find_by_id(equipment_id)
    if not item:
        raise ValueError("Equipment not found")
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

    quantity = data.get("quantity", 1)
    if not isinstance(quantity, int) or quantity < 1:
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

    quantity = data.get("quantity", 1)
    if not isinstance(quantity, int) or quantity < 1:
        raise ValueError("Quantity must be at least 1")

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

    active = borrow_repo.find_active_by_equipment(equipment_id)
    if active:
        raise ValueError("Cannot delete — this equipment has active borrows")

    equipment_repo.delete_equipment(equipment_id)


def delete_multiple(equipment_ids: list[int]) -> tuple[int, list[dict]]:
    deleted = 0
    skipped = []
    for eid in equipment_ids:
        existing = equipment_repo.find_by_id(eid)
        if not existing:
            continue
        active = borrow_repo.find_active_by_equipment(eid)
        if active:
            skipped.append({"asset_code": existing["asset_code"], "name": existing["name"]})
        else:
            equipment_repo.delete_equipment(eid)
            deleted += 1
    return deleted, skipped


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
