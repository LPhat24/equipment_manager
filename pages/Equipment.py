import streamlit as st
from datetime import date, timedelta

from services import equipment_service, borrow_service

st.title("📦 Equipment")

# --- Add Equipment (always visible at top) ---
st.markdown("---")
with st.expander("➕ Add New Equipment", expanded=False):
    with st.form("add_equipment_form", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            asset_code = st.text_input("Asset Code *")
            name = st.text_input("Name *")
            category_input = st.text_input("Category")
            location_input = st.text_input("Location")
        with fc2:
            status_input = st.selectbox("Status", ["Available", "Borrowed", "Maintenance"])
            condition_input = st.selectbox("Condition", ["Good", "Fair", "Poor", "Damaged"])
            quantity = st.number_input("Quantity", min_value=1, value=1)
            notes_input = st.text_area("Notes", height=82)

        if st.form_submit_button("Add Equipment", type="primary"):
            try:
                equipment_service.add_equipment({
                    "asset_code": asset_code,
                    "name": name,
                    "category": category_input,
                    "location": location_input,
                    "status": status_input,
                    "condition": condition_input,
                    "quantity": int(quantity),
                    "notes": notes_input,
                })
                st.success(f"Equipment '{asset_code}' added successfully!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

# --- Filter Bar ---
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

with col1:
    search = st.text_input("Search", placeholder="Search name, asset code, notes...", label_visibility="collapsed")
with col2:
    categories = ["All"] + equipment_service.get_categories()
    category = st.selectbox("Category", categories, label_visibility="collapsed")
with col3:
    status = st.selectbox("Status", ["All", "Available", "Borrowed", "Maintenance"], label_visibility="collapsed")
with col4:
    locations = ["All"] + equipment_service.get_locations()
    location = st.selectbox("Location", locations, label_visibility="collapsed")

# --- Fetch Filtered Equipment ---
filters = {}
if category != "All":
    filters["category"] = category
if status != "All":
    filters["status"] = status
if location != "All":
    filters["location"] = location
if search:
    filters["search"] = search

equipment_list = equipment_service.get_all_equipment(**filters)

# --- Equipment Table ---
STATUS_ICONS = {
    "Available": "🟢 Available",
    "Borrowed": "🔵 Borrowed",
    "Maintenance": "🟡 Maintenance",
}

CONDITION_ICONS = {
    "Good": "🟢 Good",
    "Fair": "🔵 Fair",
    "Poor": "🟠 Poor",
    "Damaged": "🔴 Damaged",
}

if not equipment_list:
    st.info("No equipment found. Use the form above to add your first item.")
else:
    table_data = [dict(row) for row in equipment_list]
    display_cols = ["asset_code", "name", "category", "location", "status", "condition", "quantity", "notes"]
    display_data = [{k: row.get(k, "") for k in display_cols} for row in table_data]

    for row in display_data:
        row["status"] = STATUS_ICONS.get(row["status"], row["status"])
        row["condition"] = CONDITION_ICONS.get(row["condition"], row["condition"])

    display_df = st.dataframe(
        display_data,
        column_config={
            "asset_code": st.column_config.TextColumn("Asset Code", width="small"),
            "name": st.column_config.TextColumn("Name", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "location": st.column_config.TextColumn("Location", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "condition": st.column_config.TextColumn("Condition", width="small"),
            "quantity": st.column_config.NumberColumn("Qty", width="small"),
            "notes": st.column_config.TextColumn("Notes", width="medium"),
        },
        selection_mode="multi-row",
        on_select="rerun",
        use_container_width=True,
        hide_index=True,
    )

    selected_rows = display_df.selection.rows

    # --- Single Item Action Panel ---
    if len(selected_rows) == 1:
        selected_idx = selected_rows[0]
        selected = equipment_list[selected_idx]

        st.markdown("---")
        st.subheader(f"{selected['asset_code']} — {selected['name']}")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Status", selected["status"])
        col_b.metric("Location", selected["location"] or "—")
        col_c.metric("Condition", selected["condition"] or "—")

        if selected["status"] == "Available":
            with st.form("borrow_form", clear_on_submit=True):
                st.markdown("**Borrow Equipment**")
                borrower_name = st.text_input("Borrower Name *")
                borrower_phone = st.text_input("Borrower Phone *")
                form_col1, form_col2 = st.columns(2)
                with form_col1:
                    borrow_date = st.date_input("Borrow Date", value=date.today())
                with form_col2:
                    expected_return = st.date_input("Expected Return Date", value=date.today() + timedelta(days=7))
                notes = st.text_area("Notes", height=68)

                if st.form_submit_button("Confirm Borrow", type="primary"):
                    if not borrower_name.strip():
                        st.error("Please enter borrower name.")
                    elif not borrower_phone.strip():
                        st.error("Please enter borrower phone.")
                    else:
                        try:
                            borrow_service.borrow_equipment(
                                equipment_id=selected["id"],
                                borrower_name=borrower_name,
                                borrower_phone=borrower_phone,
                                borrow_date=borrow_date.isoformat(),
                                expected_return_date=expected_return.isoformat(),
                                notes=notes,
                            )
                            st.success("Equipment borrowed successfully!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

        elif selected["status"] == "Borrowed":
            active = borrow_service.get_active_borrow_for(selected["id"])
            if active:
                st.info(
                    f"**Borrowed by:** {active['borrower_name']}  |  "
                    f"**Since:** {active['borrow_date']}  |  "
                    f"**Expected return:** {active['expected_return_date']}"
                )
            if st.button("Return Equipment", type="primary"):
                try:
                    borrow_service.return_equipment(active["id"])
                    st.success("Equipment returned successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        else:
            st.warning("This equipment is currently under maintenance — no actions available.")

        # --- Single Delete ---
        st.markdown("---")
        st.subheader(f"Delete {selected['asset_code']}")

        has_active = borrow_service.get_active_borrow_for(selected["id"])
        if has_active:
            st.warning("Cannot delete — this equipment has active borrows. Return it first.")
        else:
            st.info("Borrow history for this equipment will be preserved after deletion.")
            confirm = st.checkbox("I confirm I want to delete this equipment permanently")
            if st.button("Delete Equipment", type="primary", disabled=not confirm):
                try:
                    equipment_service.delete_equipment(selected["id"])
                    st.success(f"Equipment '{selected['asset_code']}' deleted.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    # --- Bulk Actions Panel ---
    elif len(selected_rows) > 1:
        selected_items = [equipment_list[i] for i in selected_rows]

        # --- Bulk Borrow ---
        st.markdown("---")
        st.subheader(f"📦 Bulk Borrow ({len(selected_items)} items)")

        borrowable = []
        borrow_blocked = []
        for item in selected_items:
            if item["status"] == "Available":
                borrowable.append(item)
            else:
                borrow_blocked.append(item)

        if borrowable:
            st.markdown("**Items available to borrow:**")
            for item in borrowable:
                st.markdown(f"  ✅ `{item['asset_code']}` — {item['name']}")

        if borrow_blocked:
            st.markdown("**Skipped (not available):**")
            for item in borrow_blocked:
                st.markdown(f"  ❌ `{item['asset_code']}` — {item['name']} ({item['status']})")

        if borrowable:
            with st.form("bulk_borrow_form", clear_on_submit=False):
                st.markdown("**Borrow Details** (shared for all items)")
                borrower_name = st.text_input("Borrower Name *")
                borrower_phone = st.text_input("Borrower Phone *")
                bc1, bc2 = st.columns(2)
                with bc1:
                    borrow_date = st.date_input("Borrow Date", value=date.today())
                with bc2:
                    expected_return = st.date_input("Expected Return Date", value=date.today() + timedelta(days=7))
                notes = st.text_area("Notes", height=68)

                if st.form_submit_button(f"Confirm Borrow {len(borrowable)} Equipment", type="primary"):
                    if not borrower_name.strip():
                        st.error("Please enter borrower name.")
                    elif not borrower_phone.strip():
                        st.error("Please enter borrower phone.")
                    else:
                        ids_to_borrow = [item["id"] for item in borrowable]
                        borrowed, skipped = borrow_service.borrow_multiple(
                            ids_to_borrow,
                            borrower_name,
                            borrower_phone,
                            borrow_date.isoformat(),
                            expected_return.isoformat(),
                            notes,
                        )
                        if borrowed > 0:
                            st.success(f"Borrowed **{borrowed}** equipment item(s).")
                        if skipped:
                            st.warning(
                                f"{len(skipped)} item(s) skipped: "
                                + ", ".join(s["asset_code"] for s in skipped)
                            )
                        st.rerun()
        else:
            st.info("No items available to borrow from the selection.")

        # --- Bulk Delete ---
        st.markdown("---")
        st.subheader(f"🗑️ Bulk Delete ({len(selected_items)} items)")

        deletable = []
        delete_blocked = []
        for item in selected_items:
            active = borrow_service.get_active_borrow_for(item["id"])
            if active:
                delete_blocked.append(item)
            else:
                deletable.append(item)

        if deletable:
            st.markdown("**Items to delete:**")
            for item in deletable:
                st.markdown(f"  ✅ `{item['asset_code']}` — {item['name']}")

        if delete_blocked:
            st.markdown("**Skipped (active borrows):**")
            for item in delete_blocked:
                st.markdown(f"  ❌ `{item['asset_code']}` — {item['name']}")

        st.info(
            f"{len(deletable)} item(s) will be deleted"
            + (f", {len(delete_blocked)} skipped" if delete_blocked else "")
            + "."
        )

        if deletable:
            st.caption("Borrow history for deleted items will be preserved.")
            confirm_bulk = st.checkbox(
                f"I confirm I want to delete {len(deletable)} equipment item(s) permanently"
            )
            if st.button(
                f"Delete {len(deletable)} Equipment", type="primary", disabled=not confirm_bulk
            ):
                ids_to_delete = [item["id"] for item in deletable]
                deleted, skipped = equipment_service.delete_multiple(ids_to_delete)
                if deleted > 0:
                    st.success(f"Deleted **{deleted}** equipment item(s).")
                if skipped:
                    st.warning(
                        f"{len(skipped)} item(s) skipped: "
                        + ", ".join(s["asset_code"] for s in skipped)
                    )
                st.rerun()
