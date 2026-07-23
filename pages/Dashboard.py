import streamlit as st
import altair as alt
import pandas as pd
from collections import Counter
from datetime import date

from services import history_service, equipment_service, borrow_service
from utils.helpers import get_status
from utils.styling import apply_full_width

apply_full_width()

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
    total_days = sum(
        (date.today() - date.fromisoformat(r["expected_return_date"])).days
        for r in overdue
    )
    st.warning(
        f"⚠ **{len(overdue)}** item(s) overdue — **{total_days}** total days overdue! "
        f"Go to [⚠ Overdue](/Overdue) to view contact list."
    )

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
        df = pd.DataFrame(list(category_counts.items()), columns=["category", "count"])
        chart = alt.Chart(df).mark_arc().encode(
            theta=alt.Theta("count", type="quantitative"),
            color=alt.Color("category", type="nominal", title="Category"),
            tooltip=["category", "count"],
        ).properties(width=300, height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No equipment data.")

with chart_col2:
    st.subheader("Equipment by Location")
    if all_items:
        location_counts = Counter(
            item["location"] or "Unassigned" for item in all_items
        )
        df = pd.DataFrame(list(location_counts.items()), columns=["location", "count"])
        chart = alt.Chart(df).mark_arc().encode(
            theta=alt.Theta("count", type="quantitative"),
            color=alt.Color("location", type="nominal", title="Location"),
            tooltip=["location", "count"],
        ).properties(width=300, height=300)
        st.altair_chart(chart, use_container_width=True)
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
            "Phone": record["borrower_phone"],
            "Qty": record["borrow_quantity"],
            "Borrowed": record["borrow_date"],
            "Due": record["expected_return_date"],
            "Returned": record["actual_return_date"] or "—",
            "Status": status,
            "Notes": record["notes"] or "—",
        })

    st.dataframe(
        activity_data,
        column_config={
            "Asset Code": st.column_config.TextColumn("Asset Code", width="small"),
            "Equipment": st.column_config.TextColumn("Equipment", width="medium"),
            "Borrower": st.column_config.TextColumn("Borrower", width="medium"),
            "Phone": st.column_config.TextColumn("Phone", width="small"),
            "Qty": st.column_config.NumberColumn("Qty", width="small"),
            "Borrowed": st.column_config.TextColumn("Borrowed", width="small"),
            "Due": st.column_config.TextColumn("Due", width="small"),
            "Returned": st.column_config.TextColumn("Returned", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Notes": st.column_config.TextColumn("Notes", width="medium"),
        },
        use_container_width=True,
        hide_index=True,
    )
