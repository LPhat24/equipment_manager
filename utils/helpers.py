"""Shared utility functions for the Lab Equipment Manager."""


def get_status(record: dict | object, today_str: str) -> str:
    """Compute borrow record status based on dates.

    Returns one of: "Returned", "Overdue", "Active".
    """
    if record["actual_return_date"]:
        return "Returned"
    elif record["expected_return_date"] < today_str:
        return "Overdue"
    else:
        return "Active"
