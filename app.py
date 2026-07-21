import streamlit as st

from database.schema import init_db
from services import history_service

st.set_page_config(
    page_title="Lab Equipment Manager",
    page_icon="🔬",
    layout="wide",
)

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
    init_db()
    st.info("Database initialized. Navigate to **⚙️ Settings** to load sample data.")

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
| **⚙️ Settings** | Import/export CSV, load sample data, manage database |
""")
