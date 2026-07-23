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
            "category": record["category"],
            "location": record["location"],
            "qty": record["borrow_quantity"],
            "borrowed_since": record["borrow_date"],
            "expected_return": record["expected_return_date"],
            "days_overdue": days_overdue,
            "overdue": "⚠ Overdue" if status == "Overdue" else "",
            "notes": record["notes"] or "",
            "_id": record["id"],
        })

    overdue_count = sum(1 for r in rows if r["overdue"])
    if overdue_count:
        st.warning(f"{overdue_count} item(s) overdue — return requested!")

    # --- Filter Bar ---
    unique_borrowers = sorted(set(r["borrower"] for r in rows))
    unique_names = sorted(set(r["equipment_name"] for r in rows))
    unique_categories = sorted(set(r["category"] for r in rows if r["category"]))
    unique_locations = sorted(set(r["location"] for r in rows if r["location"]))

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        filter_borrower = st.selectbox("Borrower", ["All"] + unique_borrowers, key="ret_borrower")
    with fc2:
        filter_name = st.selectbox("Equipment", ["All"] + unique_names, key="ret_name")
    with fc3:
        filter_category = st.selectbox("Category", ["All"] + unique_categories, key="ret_category")
    with fc4:
        filter_location = st.selectbox("Location", ["All"] + unique_locations, key="ret_location")

    # --- Apply Filters ---
    filtered = list(rows)
    if filter_borrower != "All":
        filtered = [r for r in filtered if r["borrower"] == filter_borrower]
    if filter_name != "All":
        filtered = [r for r in filtered if r["equipment_name"] == filter_name]
    if filter_category != "All":
        filtered = [r for r in filtered if r["category"] == filter_category]
    if filter_location != "All":
        filtered = [r for r in filtered if r["location"] == filter_location]

    if not filtered:
        st.info("No items match the current filters.")
    else:
        # --- Active Borrows Table (multi-select) ---
        display_cols = ["asset_code", "equipment_name", "borrower", "phone", "category", "location", "qty", "borrowed_since", "expected_return", "days_overdue", "overdue", "notes"]
        display_data = [{k: r[k] for k in display_cols} for r in filtered]

        table_df = st.dataframe(
            display_data,
            column_config={
                "asset_code": st.column_config.TextColumn("Asset Code", width="small"),
                "equipment_name": st.column_config.TextColumn("Equipment", width="medium"),
                "borrower": st.column_config.TextColumn("Borrower", width="medium"),
                "phone": st.column_config.TextColumn("Phone", width="small"),
                "category": st.column_config.TextColumn("Category", width="small"),
                "location": st.column_config.TextColumn("Location", width="small"),
                "qty": st.column_config.NumberColumn("Qty", width="small"),
                "borrowed_since": st.column_config.TextColumn("Since", width="small"),
                "expected_return": st.column_config.TextColumn("Due", width="small"),
                "days_overdue": st.column_config.TextColumn("Days Overdue", width="small"),
                "overdue": st.column_config.TextColumn("", width="small"),
                "notes": st.column_config.TextColumn("Notes", width="medium"),
            },
            selection_mode="multi-row",
            on_select="rerun",
            use_container_width=True,
            hide_index=True,
        )

        selected_rows = table_df.selection.rows

        # --- Return Selected ---
        if selected_rows:
            st.markdown("---")
            selected_items = [filtered[i] for i in selected_rows]
            selected_ids = [item["_id"] for item in selected_items]

            st.subheader(f"📥 Return Selected ({len(selected_items)} item(s))")

            for item in selected_items:
                st.markdown(f"  • `{item['asset_code']}` — {item['equipment_name']} ({item['borrower']}, qty {item['qty']})")

            confirm_selected = st.checkbox("I confirm I want to return the selected items")
            if st.button(f"Return {len(selected_items)} Item(s)", type="primary", disabled=not confirm_selected):
                returned, skipped = borrow_service.return_multiple(selected_ids)
                if returned > 0:
                    st.success(f"Returned **{returned}** item(s) successfully.")
                if skipped:
                    st.warning(
                        f"{len(skipped)} item(s) skipped: "
                        + ", ".join(s["asset_code"] for s in skipped)
                    )
                st.rerun()

        # --- Return All by Filter ---
        has_filter = any([
            filter_borrower != "All",
            filter_name != "All",
            filter_category != "All",
            filter_location != "All",
        ])

        if has_filter:
            st.markdown("---")
            st.subheader("📥 Return All Matching Filter")

            filter_desc_parts = []
            if filter_borrower != "All":
                filter_desc_parts.append(f"Borrower: {filter_borrower}")
            if filter_name != "All":
                filter_desc_parts.append(f"Equipment: {filter_name}")
            if filter_category != "All":
                filter_desc_parts.append(f"Category: {filter_category}")
            if filter_location != "All":
                filter_desc_parts.append(f"Location: {filter_location}")
            filter_desc = " | ".join(filter_desc_parts)

            st.markdown(f"**{len(filtered)}** item(s) match: {filter_desc}")

            confirm_all = st.checkbox("I confirm I want to return ALL matching items")
            if st.button(f"Return All {len(filtered)} Matching Items", type="primary", disabled=not confirm_all):
                all_ids = [item["_id"] for item in filtered]
                returned, skipped = borrow_service.return_multiple(all_ids)
                if returned > 0:
                    st.success(f"Returned **{returned}** item(s) successfully.")
                if skipped:
                    st.warning(
                        f"{len(skipped)} item(s) skipped: "
                        + ", ".join(s["asset_code"] for s in skipped)
                    )
                st.rerun()

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
