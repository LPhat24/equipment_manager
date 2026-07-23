import streamlit as st
from datetime import date

from services import borrow_service
from utils.styling import apply_full_width

apply_full_width()

st.title("⚠ Overdue Equipment")

# --- Load Overdue Records ---
active_borrows = borrow_service.get_active_borrows()
today = date.today()
today_str = today.isoformat()

overdue = [r for r in active_borrows if r["expected_return_date"] < today_str]

if not overdue:
    st.info("No overdue equipment — all items returned on time.")
    st.stop()

# --- Compute Days Overdue ---
overdue_data = []
for record in overdue:
    due = date.fromisoformat(record["expected_return_date"])
    days_overdue = (today - due).days
    overdue_data.append({
        "asset_code": record["asset_code"],
        "equipment_name": record["equipment_name"],
        "borrower_name": record["borrower_name"],
        "borrower_phone": record["borrower_phone"],
        "borrow_quantity": record["borrow_quantity"],
        "borrow_date": record["borrow_date"],
        "expected_return_date": record["expected_return_date"],
        "days_overdue": days_overdue,
    })

overdue_data.sort(key=lambda x: x["days_overdue"], reverse=True)
total_days = sum(r["days_overdue"] for r in overdue_data)

# --- Summary Warning ---
st.warning(
    f"⚠ **{len(overdue_data)}** item(s) currently overdue — "
    f"**{total_days}** total days overdue"
)

# --- Overdue Table ---
st.subheader("📋 Overdue Items")

display_rows = [
    {
        "Asset Code": r["asset_code"],
        "Equipment": r["equipment_name"],
        "Borrower": r["borrower_name"],
        "Phone": r["borrower_phone"],
        "Qty": r["borrow_quantity"],
        "Borrowed": r["borrow_date"],
        "Due": r["expected_return_date"],
        "Days Overdue": str(r["days_overdue"]),
    }
    for r in overdue_data
]

st.dataframe(
    display_rows,
    column_config={
        "Asset Code": st.column_config.TextColumn("Asset Code", width="small"),
        "Equipment": st.column_config.TextColumn("Equipment", width="medium"),
        "Borrower": st.column_config.TextColumn("Borrower", width="medium"),
        "Phone": st.column_config.TextColumn("Phone", width="small"),
        "Qty": st.column_config.NumberColumn("Qty", width="small"),
        "Borrowed": st.column_config.TextColumn("Borrowed", width="small"),
        "Due": st.column_config.TextColumn("Due", width="small"),
        "Days Overdue": st.column_config.TextColumn("Days Overdue", width="small"),
    },
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# --- Contact List ---
st.subheader("📞 Contact List")

# Messaging format
msg_lines = [
    "=== OVERDUE EQUIPMENT CONTACT LIST ===",
    f"Date: {today_str}",
    "",
]
for i, r in enumerate(overdue_data, 1):
    msg_lines.append(f"{i}. {r['borrower_name']} — {r['borrower_phone']}")
    msg_lines.append(
        f"   {r['asset_code']} {r['equipment_name']} (qty {r['borrow_quantity']}) | "
        f"Due: {r['expected_return_date']} | {r['days_overdue']} days overdue"
    )
    msg_lines.append("")

msg_text = "\n".join(msg_lines)

col_copy, col_download = st.columns(2)

with col_copy:
    st.markdown("**Copy for messaging (WhatsApp, SMS, etc.)**")
    st.code(msg_text, language=None)

with col_download:
    st.markdown("**Download for printing (bulletin board)**")
    print_lines = [
        "================================================",
        " OVERDUE EQUIPMENT — LAB BULLETIN BOARD",
        f" Generated: {today_str}",
        "================================================",
        "",
        f"{'Asset Code':<12} {'Equipment':<18} {'Borrower':<15} {'Phone':<16} {'Qty':<5} {'Due':<12} {'Days':<5}",
        f"{'-'*12} {'-'*18} {'-'*15} {'-'*16} {'-'*5} {'-'*12} {'-'*5}",
    ]
    for r in overdue_data:
        print_lines.append(
            f"{r['asset_code']:<12} {r['equipment_name']:<18} "
            f"{r['borrower_name']:<15} {r['borrower_phone']:<16} "
            f"{r['borrow_quantity']:<5} {r['expected_return_date']:<12} {r['days_overdue']:<5}"
        )
    print_lines.append("")
    print_lines.append(f"Total overdue: {len(overdue_data)} item(s), {total_days} days")
    print_text = "\n".join(print_lines)

    st.download_button(
        label="Download Overdue Contact List (.txt)",
        data=print_text,
        file_name=f"overdue_contact_list_{today_str}.txt",
        mime="text/plain",
        type="primary",
    )
