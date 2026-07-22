import streamlit as st
from collections import defaultdict
from datetime import date

from services import history_service
from utils.helpers import get_status

st.title("📜 Borrow History")

today_str = date.today().isoformat()

# --- Load All Records ---
all_records = history_service.get_all_history()

if not all_records:
    st.info("No borrow history yet.")
    st.stop()

# --- Compute Unique Borrowers ---
unique_borrowers = sorted(set(r["borrower_name"] for r in all_records))

# --- Filter Bar ---
col1, col2, col3 = st.columns([3, 2, 2])

with col1:
    search = st.text_input("Search", placeholder="Search borrower, equipment, asset code...", label_visibility="collapsed")
with col2:
    status_filter = st.selectbox("Status", ["All", "Active", "Returned", "Overdue"], label_visibility="collapsed")
with col3:
    borrower_filter = st.selectbox("Borrower", ["All"] + unique_borrowers, label_visibility="collapsed")

# --- Apply Filters ---
filtered = list(all_records)

if search:
    term = search.strip().lower()
    filtered = [
        r for r in filtered
        if term in r["borrower_name"].lower()
        or term in r["asset_code"].lower()
        or term in r["equipment_name"].lower()
    ]

if status_filter != "All":
    filtered = [r for r in filtered if get_status(r, today_str) == status_filter]

if borrower_filter != "All":
    filtered = [r for r in filtered if r["borrower_name"] == borrower_filter]

if not filtered:
    st.info("No records match the current filters.")
    st.stop()

# --- Group by Month ---
MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}


def format_month(month_key):
    year, month = month_key.split("-")
    return f"{MONTH_NAMES[month]} {year}"


monthly = defaultdict(list)
for record in filtered:
    month_key = record["borrow_date"][:7]
    monthly[month_key].append(record)

# --- Render Timeline ---
STATUS_ICONS = {"Active": "🔵", "Returned": "✅", "Overdue": "⚠"}

for month_key in sorted(monthly.keys(), reverse=True):
    records = monthly[month_key]
    label = format_month(month_key)

    with st.expander(f"📅 {label} — {len(records)} record(s)", expanded=(month_key >= today_str[:7])):
        for record in records:
            status = get_status(record, today_str)
            icon = STATUS_ICONS[status]

            equip_info = f"`{record['asset_code']}` {record['equipment_name']}"
            borrower = record["borrower_name"]
            phone = record["borrower_phone"]
            borrow_date = record["borrow_date"]
            due = record["expected_return_date"]
            returned = record["actual_return_date"]

            line1 = f"**{borrow_date}** — {equip_info}"
            line2 = f"Borrowed by **{borrower}** (📞 {phone}) | Due {due}"

            if returned:
                line2 += f" — {icon} {status} ({returned})"
            elif status == "Overdue":
                days_overdue = (date.today() - date.fromisoformat(due)).days
                line2 += f" — {icon} {status} (**{days_overdue} days**)"
            else:
                line2 += f" — {icon} {status}"

            st.markdown(f"{line1}  \n{line2}")

            if record["notes"]:
                st.caption(f"📝 {record['notes']}")
