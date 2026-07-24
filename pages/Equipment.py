import streamlit as st
from datetime import date, timedelta

from services import equipment_service, borrow_service
from utils.styling import apply_full_width

apply_full_width()

st.title("📦 Equipment")

# --- Add Equipment (always visible at top) ---
st.markdown("---")
with st.expander("➕ Add New Equipment", expanded=False):
    with st.form("add_equipment_form", clear_on_submit=False):
        fc1, fc2 = st.columns(2)
        with fc1:
            asset_code = st.text_input("Asset Code *")
            name = st.text_input("Name *")
            category_input = st.text_input("Category")
            location_input = st.text_input("Location")
        with fc2:
            status_input = st.selectbox("Status", ["Available", "Maintenance"])
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
    all_categories = equipment_service.get_categories()
    categories = st.multiselect("Category", all_categories, label_visibility="collapsed")
with col3:
    all_statuses = ["Available", "Borrowed", "Maintenance"]
    statuses = st.multiselect("Status", all_statuses, label_visibility="collapsed")
with col4:
    all_locations = equipment_service.get_locations()
    locations = st.multiselect("Location", all_locations, label_visibility="collapsed")

# --- Fetch Filtered Equipment ---
filters = {}
if categories:
    filters["categories"] = categories
if statuses:
    filters["statuses"] = statuses
if locations:
    filters["locations"] = locations
if search:
    filters["search"] = search

equipment_list = equipment_service.get_all_equipment(**filters)

# --- Equipment Table ---
STATUS_ICONS = {
    "Available": "🟢 Available",
    "Borrowed": "🔴 Borrowed",
    "Maintenance": "🟡 Maintenance",
}

CONDITION_ICONS = {
    "Good": "🟢 Good",
    "Fair": "🔵 Fair",
    "Poor": "🟠 Poor",
    "Damaged": "🔴 Damaged",
}


def _compute_status(item):
    if item["status"] == "Maintenance":
        return "Maintenance"
    return "Available" if item["available_quantity"] > 0 else "Borrowed"


if not equipment_list:
    st.info("No equipment found. Use the form above to add your first item.")
else:
    table_data = [dict(row) for row in equipment_list]

    display_data = []
    for row in table_data:
        computed = _compute_status(row)
        display_data.append({
            "asset_code": row["asset_code"],
            "name": row["name"],
            "category": row["category"],
            "location": row["location"],
            "status": STATUS_ICONS.get(computed, computed),
            "condition": CONDITION_ICONS.get(row["condition"], row["condition"]),
            "available": f"{row['available_quantity']}/{row['quantity']}",
            "notes": row["notes"],
        })

    display_df = st.dataframe(
        display_data,
        column_config={
            "asset_code": st.column_config.TextColumn("Asset Code", width="small"),
            "name": st.column_config.TextColumn("Name", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "location": st.column_config.TextColumn("Location", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "condition": st.column_config.TextColumn("Condition", width="small"),
            "available": st.column_config.TextColumn("Available", width="small"),
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
        computed_status = _compute_status(selected)

        st.markdown("---")
        st.subheader(f"{selected['asset_code']} — {selected['name']}")

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Status", STATUS_ICONS.get(computed_status, computed_status))
        col_b.metric("Location", selected["location"] or "—")
        col_c.metric("Condition", selected["condition"] or "—")
        col_d.metric("Available", f"{selected['available_quantity']} / {selected['quantity']}")

        # --- Edit Equipment ---
        with st.expander("✏️ Edit Equipment", expanded=False):
            with st.form("edit_equipment_form", clear_on_submit=False):
                ec1, ec2 = st.columns(2)
                with ec1:
                    edit_asset_code = st.text_input("Asset Code *", value=selected["asset_code"])
                    edit_name = st.text_input("Name *", value=selected["name"])
                    edit_category = st.text_input("Category", value=selected["category"])
                    edit_location = st.text_input("Location", value=selected["location"])
                with ec2:
                    if selected["status"] == "Borrowed":
                        st.selectbox("Status", ["Borrowed"], disabled=True, key="edit_status_disabled")
                        st.info("📌 Status is set automatically when equipment is returned.")
                        edit_status = "Borrowed"
                    else:
                        edit_status = st.selectbox("Status", ["Available", "Maintenance"],
                                                    index=["Available", "Maintenance"].index(selected["status"]))
                    edit_condition = st.selectbox("Condition", ["Good", "Fair", "Poor", "Damaged"],
                                                   index=["Good", "Fair", "Poor", "Damaged"].index(selected["condition"]))
                    edit_quantity = st.number_input("Quantity", min_value=1, value=selected["quantity"])
                    edit_notes = st.text_area("Notes", value=selected["notes"], height=82)

                active_borrows = selected["quantity"] - selected["available_quantity"]
                if active_borrows > 0:
                    st.info(f"📌 {active_borrows} copy(ies) currently borrowed — quantity cannot be reduced below {active_borrows}")

                if st.form_submit_button("Save Changes", type="primary"):
                    try:
                        equipment_service.update_equipment(selected["id"], {
                            "asset_code": edit_asset_code,
                            "name": edit_name,
                            "category": edit_category,
                            "location": edit_location,
                            "status": edit_status,
                            "condition": edit_condition,
                            "quantity": int(edit_quantity),
                            "notes": edit_notes,
                        })
                        st.success(f"Equipment '{edit_asset_code}' updated successfully!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        show_borrow_form = False
        is_maintenance_borrow = False

        if selected["available_quantity"] <= 0:
            st.info("All copies are currently borrowed.")
        elif computed_status == "Available":
            show_borrow_form = True
        elif computed_status == "Maintenance":
            st.warning("⚠️ This equipment is currently under maintenance. Borrowing is not recommended.")
            if st.checkbox("I understand and want to proceed anyway", key=f"maint_{selected['id']}"):
                show_borrow_form = True
                is_maintenance_borrow = True

        if show_borrow_form:
            with st.form("borrow_form", clear_on_submit=False):
                st.markdown("**Borrow Equipment**")
                borrower_name = st.text_input("Borrower Name *")
                borrower_phone = st.text_input("Borrower Phone *")
                borrow_qty = st.number_input(
                    "Quantity to borrow",
                    min_value=1,
                    max_value=selected["available_quantity"],
                    value=1,
                )
                form_col1, form_col2 = st.columns(2)
                with form_col1:
                    borrow_date = st.date_input("Borrow Date", value=date.today())
                with form_col2:
                    max_return = borrow_date + timedelta(days=90)
                    expected_return = st.date_input("Expected Return Date", value=min(date.today() + timedelta(days=7), max_return), max_value=max_return)
                notes = st.text_area("Notes", height=68)

                if st.form_submit_button("Confirm Borrow", type="primary"):
                    if len(borrower_name.strip()) < 2:
                        st.error("Name must be at least 2 characters.")
                    elif len(borrower_phone.strip().replace("-", "").replace(" ", "")) < 8:
                        st.error("Phone must be at least 8 digits.")
                    else:
                        try:
                            borrow_service.borrow_equipment(
                                equipment_id=selected["id"],
                                borrower_name=borrower_name,
                                borrower_phone=borrower_phone,
                                borrow_date=borrow_date.isoformat(),
                                expected_return_date=expected_return.isoformat(),
                                notes=notes,
                                borrow_quantity=int(borrow_qty),
                                force=is_maintenance_borrow,
                            )
                            st.success("Equipment borrowed successfully!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

        if computed_status in ("Borrowed", "Maintenance"):
            active_borrows = borrow_service.get_active_borrows_for(selected["id"])
            if active_borrows:
                st.markdown("**Active Borrows:**")
                for rec in active_borrows:
                    bc1, bc2 = st.columns([5, 1])
                    with bc1:
                        info_text = (
                            f"**{rec['borrower_name']}** — qty {rec['borrow_quantity']}  |  "
                            f"Since: {rec['borrow_date']}  |  Due: {rec['expected_return_date']}"
                        )
                        if rec["notes"]:
                            info_text += f"  |  📝 {rec['notes']}"
                        st.info(info_text)
                    with bc2:
                        if st.button("Return", key=f"ret_{rec['id']}", type="primary"):
                            try:
                                borrow_service.return_equipment(rec["id"])
                                st.success("Returned successfully!")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
            else:
                st.info("All copies returned.")

        # --- Single Delete ---
        st.markdown("---")
        st.subheader(f"Delete {selected['asset_code']}")

        has_active = selected["available_quantity"] < selected["quantity"]
        if has_active:
            st.warning("Cannot delete — this equipment has active borrows. Return all copies first.")
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
        maintenance = []
        borrow_blocked = []
        for item in selected_items:
            if item["available_quantity"] <= 0:
                borrow_blocked.append(item)
            elif item["status"] == "Maintenance":
                maintenance.append(item)
            else:
                borrowable.append(item)

        if borrow_blocked:
            st.warning(
                f"⚠️ {len(borrow_blocked)} item(s) have no available copies and will be skipped:"
            )
            for item in borrow_blocked:
                st.markdown(f"  ❌ `{item['asset_code']}` — {item['name']} (0/{item['quantity']} available)")

        if borrowable:
            st.markdown("**Items available to borrow:**")
            for item in borrowable:
                st.markdown(f"  ✅ `{item['asset_code']}` — {item['name']} ({item['available_quantity']}/{item['quantity']} available)")

        if maintenance:
            st.warning(
                f"⚠️ {len(maintenance)} item(s) are under maintenance and not recommended for borrowing:"
            )
            for item in maintenance:
                st.markdown(f"  🟡 `{item['asset_code']}` — {item['name']} ({item['available_quantity']}/{item['quantity']} available)")

        if borrowable or maintenance:
            with st.form("bulk_borrow_form", clear_on_submit=False):
                st.markdown("**Borrow Details**")
                borrower_name = st.text_input("Borrower Name *")
                borrower_phone = st.text_input("Borrower Phone *")
                bc1, bc2 = st.columns(2)
                with bc1:
                    borrow_date = st.date_input("Borrow Date", value=date.today())
                with bc2:
                    max_return = borrow_date + timedelta(days=90)
                    expected_return = st.date_input("Expected Return Date", value=min(date.today() + timedelta(days=7), max_return), max_value=max_return)
                notes = st.text_area("Notes", height=68)

                st.markdown("**Select quantity for each item:**")
                for item in borrowable:
                    ic1, ic2 = st.columns([4, 1])
                    with ic1:
                        st.markdown(f"`{item['asset_code']}` — {item['name']} ({item['available_quantity']} avail)")
                    with ic2:
                        st.number_input(
                            "Qty",
                            min_value=1,
                            max_value=item["available_quantity"],
                            value=1,
                            key=f"bulk_qty_{item['id']}",
                            label_visibility="collapsed",
                        )

                for item in maintenance:
                    ic1, ic2 = st.columns([4, 1])
                    with ic1:
                        st.markdown(f"🟡 `{item['asset_code']}` — {item['name']} ({item['available_quantity']} avail, maintenance)")
                    with ic2:
                        st.number_input(
                            "Qty",
                            min_value=1,
                            max_value=item["available_quantity"],
                            value=1,
                            key=f"bulk_qty_{item['id']}",
                            label_visibility="collapsed",
                        )

                include_maintenance = False
                if maintenance:
                    include_maintenance = st.checkbox(
                        "I understand these items are under maintenance and want to include them"
                    )

                total_borrowable = len(borrowable) + (len(maintenance) if include_maintenance else 0)
                if total_borrowable > 0:
                    if st.form_submit_button(f"Confirm Borrow {total_borrowable} Equipment", type="primary"):
                        if len(borrower_name.strip()) < 2:
                            st.error("Name must be at least 2 characters.")
                        elif len(borrower_phone.strip().replace("-", "").replace(" ", "")) < 8:
                            st.error("Phone must be at least 8 digits.")
                        else:
                            equipment_map = {
                                item["id"]: st.session_state[f"bulk_qty_{item['id']}"]
                                for item in borrowable
                            }
                            if include_maintenance:
                                for item in maintenance:
                                    equipment_map[item["id"]] = st.session_state[f"bulk_qty_{item['id']}"]
                            borrowed, skipped = borrow_service.borrow_multiple(
                                equipment_map,
                                borrower_name,
                                borrower_phone,
                                borrow_date.isoformat(),
                                expected_return.isoformat(),
                                notes,
                                force=include_maintenance,
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
            if item["available_quantity"] < item["quantity"]:
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
