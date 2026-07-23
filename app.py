import os

import streamlit as st
from dotenv import load_dotenv
from datetime import date

from database.schema import init_db
from services import history_service, borrow_service
from utils.styling import apply_full_width

load_dotenv()

try:
    if "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except Exception:
    pass

st.set_page_config(
    page_title="Lab Equipment Manager",
    page_icon="🔬",
    layout="wide",
)

apply_full_width()

st.title("🔬 Lab Equipment Manager")

st.markdown(
    "A lightweight inventory system for managing laboratory equipment — "
    "know what you have, where it is, and who has it."
)

# --- Quick Stats ---
try:
    stats = history_service.get_statistics()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", stats["total_items"])
    col2.metric("Available", stats["available"])
    col3.metric("Borrowed", stats["borrowed"])
    col4.metric("Maintenance", stats["maintenance"])
except Exception:
    try:
        init_db()
        st.info("Database initialized. Navigate to **⚙️ Settings** to load sample data.")
    except Exception as e:
        st.error(f"Could not connect to database. Check your DATABASE_URL. Error: {e}")

# --- Overdue Warning ---
try:
    active_borrows = borrow_service.get_active_borrows()
    today = date.today()
    today_str = today.isoformat()
    overdue_items = [
        r for r in active_borrows
        if r["expected_return_date"] < today_str
    ]
    if overdue_items:
        total_days = sum(
            (today - date.fromisoformat(r["expected_return_date"])).days
            for r in overdue_items
        )
        st.warning(
            f"⚠ **{len(overdue_items)}** item(s) overdue — **{total_days}** total days overdue! "
            f"Go to [⚠ Overdue](/Overdue) to view contact list."
        )
except Exception:
    pass

st.markdown("---")

# --- Page Guide ---
st.subheader("Pages")

st.markdown("""
| Page | Description |
|------|-------------|
| **📦 Equipment** | Browse, search, filter, add, borrow, and return equipment |
| **🔄 Borrow & Return** | View active borrows, process returns, borrow available items |
| **📊 Dashboard** | Overview statistics, category/location charts, recent activity |
| **📜 History** | Timeline of all borrow records with search and filters |
| **⚠ Overdue** | View overdue equipment and borrower contact list |
| **⚙️ Settings** | Import/export CSV, load sample data, manage database |
""")
