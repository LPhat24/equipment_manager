import streamlit as st
from collections import Counter
from datetime import date

from services import history_service, equipment_service, borrow_service
from utils.helpers import get_status

st.title("📊 Dashboard")

# --- Summary Cards ---
stats = history_service.get_statistics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Items", stats["total_items"])
col2.metric("Available", stats["available"])
col3.metric("Borrowed", stats["borrowed"])
col4.metric("Maintenance", stats["maintenance"])

# --- Overdue Warning ---
active_borrows = borrow_service.get_active_borrows()
today = date.today().isoformat()
overdue = [r for r in active_borrows if r["expected_return_date"] < today]
if overdue:
    st.warning(f"⚠ **{len(overdue)}** item(s) overdue — return requested!")

st.markdown("---")

# --- Charts ---
chart_col1, chart_col2 = st.columns(2)

all_items = equipment_service.get_all_equipment()

with chart_col1:
    st.subheader("Equipment by Category")
    if all_items:
        category_counts = Counter(
            item["category"] or "Uncategorized" for item in all_items
        )
        st.bar_chart(category_counts)
    else:
        st.info("No equipment data.")

with chart_col2:
    st.subheader("Equipment by Location")
    if all_items:
        location_counts = Counter(
            item["location"] or "Unassigned" for item in all_items
        )
        st.bar_chart(location_counts)
    else:
        st.info("No equipment data.")

st.markdown("---")

# --- Recent Borrow Activity ---
st.subheader("📋 Recent Borrow Activity")

history = history_service.get_all_history()

if not history:
    st.info("No borrow history yet.")
else:
    recent = history[:10]

    activity_data = []
    for record in recent:
        status = get_status(record, today)

        activity_data.append({
            "Asset Code": record["asset_code"],
            "Equipment": record["equipment_name"],
            "Borrower": record["borrower_name"],
            "Borrowed": record["borrow_date"],
            "Due": record["expected_return_date"],
            "Returned": record["actual_return_date"] or "—",
            "Status": status,
        })

    st.dataframe(
        activity_data,
        column_config={
            "Asset Code": st.column_config.TextColumn("Asset Code", width="small"),
            "Equipment": st.column_config.TextColumn("Equipment", width="medium"),
            "Borrower": st.column_config.TextColumn("Borrower", width="medium"),
            "Borrowed": st.column_config.TextColumn("Borrowed", width="small"),
            "Due": st.column_config.TextColumn("Due", width="small"),
            "Returned": st.column_config.TextColumn("Returned", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )
