"""Borrow history table data access operations."""

import sqlite3

from database.db import fetch_all, fetch_one, insert, update


def find_by_id(record_id: int) -> sqlite3.Row | None:
    return fetch_one("SELECT * FROM borrow_history WHERE id = ?", (record_id,))


def find_active_by_equipment(equipment_id: int) -> sqlite3.Row | None:
    return fetch_one(
        "SELECT * FROM borrow_history WHERE equipment_id = ? AND actual_return_date IS NULL",
        (equipment_id,),
    )


def find_all_active() -> list[sqlite3.Row]:
    return fetch_all(
        """SELECT bh.id, bh.equipment_id, bh.borrower_name, bh.borrow_date,
                  bh.expected_return_date, bh.actual_return_date, bh.notes,
                  COALESCE(bh.asset_code, e.asset_code, '') AS asset_code,
                  COALESCE(bh.equipment_name, e.name, '') AS equipment_name
           FROM borrow_history bh
           LEFT JOIN equipment e ON bh.equipment_id = e.id
           WHERE bh.actual_return_date IS NULL
           ORDER BY bh.borrow_date"""
    )


def find_by_equipment(equipment_id: int) -> list[sqlite3.Row]:
    return fetch_all(
        "SELECT * FROM borrow_history WHERE equipment_id = ? ORDER BY borrow_date DESC",
        (equipment_id,),
    )


def find_all() -> list[sqlite3.Row]:
    return fetch_all(
        """SELECT bh.id, bh.equipment_id, bh.borrower_name, bh.borrow_date,
                  bh.expected_return_date, bh.actual_return_date, bh.notes,
                  COALESCE(bh.asset_code, e.asset_code, '') AS asset_code,
                  COALESCE(bh.equipment_name, e.name, '') AS equipment_name
           FROM borrow_history bh
           LEFT JOIN equipment e ON bh.equipment_id = e.id
           ORDER BY bh.created_at DESC"""
    )


def insert_record(data: dict) -> int:
    return insert("borrow_history", data)


def mark_returned(record_id: int, actual_return_date: str) -> int:
    return update(
        "UPDATE borrow_history SET actual_return_date = ? WHERE id = ?",
        (actual_return_date, record_id),
    )


def delete_all() -> int:
    return update("DELETE FROM borrow_history")


def count_active() -> int:
    row = fetch_one(
        "SELECT COUNT(*) AS cnt FROM borrow_history WHERE actual_return_date IS NULL"
    )
    return row["cnt"] if row else 0
