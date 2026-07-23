import streamlit as st
from datetime import date, timedelta

from services import equipment_service, borrow_service
from utils.helpers import get_status
from utils.styling import apply_full_width

apply_full_width()

st.title("🔄 Borrow & Return")

# --- Active Borrows ---
st.subheader("📋 Active Borrows")

active_borrows = borrow_service.get_active_borrows()

if not active_borrows:
    st.info("No items currently borrowed.")
else:
    today = date.today()
    today_str = today.isoformat()

    rows = []
    for record in active_borrows:
        status = get_status(record, today_str)
        days_overdue = ""
        if status == "Overdue":
            days_overdue = str((today - date.fromisoformat(record["expected_return_date"])).days)
        rows.append({
            "asset_code": record["asset_code"],
            "equipment_name": record["equipment_name"],
            "borrower": record["borrower_name"],
            "phone": record["borrower_phone"],
            "qty": record["borrow_quantity"],
            "borrowed_since": record["borrow_date"],
            "expected_return": record["expected_return_date"],
            "days_overdue": days_overdue,
            "overdue": "⚠ Overdue" if status == "Overdue" else "",
            "_id": record["id"],
        })

    overdue_count = sum(1 for r in rows if r["overdue"])
    if overdue_count:
        st.warning(f"{overdue_count} item(s) overdue — return requested!")

    display = [
        {k: r[k] for k in ["asset_code", "equipment_name", "borrower", "phone", "qty", "borrowed_since", "expected_return", "days_overdue", "overdue"]}
        for r in rows
    ]
    st.dataframe(
        display,
        column_config={
            "asset_code": st.column_config.TextColumn("Asset Code", width="small"),
            "equipment_name": st.column_config.TextColumn("Equipment", width="medium"),
            "borrower": st.column_config.TextColumn("Borrower", width="medium"),
            "phone": st.column_config.TextColumn("Phone", width="small"),
            "qty": st.column_config.NumberColumn("Qty", width="small"),
            "borrowed_since": st.column_config.TextColumn("Since", width="small"),
            "expected_return": st.column_config.TextColumn("Due", width="small"),
            "days_overdue": st.column_config.TextColumn("Days Overdue", width="small"),
            "overdue": st.column_config.TextColumn("", width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # --- Return Section ---
    st.markdown("---")
    st.subheader("📥 Return Equipment")

    borrow_options = [
        f"{r['asset_code']} — {r['equipment_name']} ({r['borrower_name']}, qty {r['borrow_quantity']})"
        for r in active_borrows
    ]
    borrow_id_map = {
        opt: active_borrows[i]["id"]
        for i, opt in enumerate(borrow_options)
    }

    selected_option = st.selectbox("Select item to return", borrow_options, index=None, placeholder="Choose an item...")

    if selected_option:
        record_id = borrow_id_map[selected_option]
        if st.button("Return Equipment", type="primary"):
            try:
                borrow_service.return_equipment(record_id)
                st.success("Equipment returned successfully!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

# --- Borrow Section ---
st.markdown("---")
st.subheader("📦 Borrow Equipment")

available = equipment_service.get_all_equipment(statuses=["Available"])

available_with_stock = [item for item in available if item["available_quantity"] > 0]

if not available_with_stock:
    st.info("No equipment currently available to borrow.")
else:
    with st.form("borrow_form", clear_on_submit=False):
        equip_options = [
            f"{row['asset_code']} — {row['name']} ({row['available_quantity']}/{row['quantity']} available"
            + (f", {row['location']}" if row["location"] else "")
            + ")"
            for row in available_with_stock
        ]
        equip_id_map = {
            opt: available_with_stock[i]["id"]
            for i, opt in enumerate(equip_options)
        }
        equip_avail_map = {
            opt: available_with_stock[i]["available_quantity"]
            for i, opt in enumerate(equip_options)
        }

        selected_equip = st.selectbox("Equipment *", equip_options, index=None, placeholder="Select equipment...")

        borrow_qty = 1
        if selected_equip:
            max_avail = equip_avail_map[selected_equip]
            borrow_qty = st.number_input("Quantity to borrow", min_value=1, max_value=max_avail, value=1)

        borrower_name = st.text_input("Borrower Name *")
        borrower_phone = st.text_input("Borrower Phone *")

        fc1, fc2 = st.columns(2)
        with fc1:
            borrow_date = st.date_input("Borrow Date", value=date.today())
        with fc2:
            max_return = borrow_date + timedelta(days=90)
            expected_return = st.date_input("Expected Return Date", value=min(date.today() + timedelta(days=7), max_return), max_value=max_return)

        notes = st.text_area("Notes", height=68)

        if st.form_submit_button("Confirm Borrow", type="primary"):
            if not selected_equip:
                st.error("Please select equipment.")
            elif len(borrower_name.strip()) < 2:
                st.error("Name must be at least 2 characters.")
            elif len(borrower_phone.strip().replace("-", "").replace(" ", "")) < 8:
                st.error("Phone must be at least 8 digits.")
            else:
                try:
                    borrow_service.borrow_equipment(
                        equipment_id=equip_id_map[selected_equip],
                        borrower_name=borrower_name,
                        borrower_phone=borrower_phone,
                        borrow_date=borrow_date.isoformat(),
                        expected_return_date=expected_return.isoformat(),
                        notes=notes,
                        borrow_quantity=int(borrow_qty),
                    )
                    st.success("Equipment borrowed successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
