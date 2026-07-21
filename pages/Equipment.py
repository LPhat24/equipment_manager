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
if not equipment_list:
    st.info("No equipment found. Use the form above to add your first item.")
else:
    table_data = [dict(row) for row in equipment_list]
    display_cols = ["asset_code", "name", "category", "location", "status", "condition", "quantity", "notes"]
    display_data = [{k: row.get(k, "") for k in display_cols} for row in table_data]

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
        selection_mode="single-row",
        on_select="rerun",
        use_container_width=True,
        hide_index=True,
    )

    # --- Action Panel ---
    if display_df.selection.rows:
        selected_idx = display_df.selection.rows[0]
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
                form_col1, form_col2 = st.columns(2)
                with form_col1:
                    borrow_date = st.date_input("Borrow Date", value=date.today())
                with form_col2:
                    expected_return = st.date_input("Expected Return Date", value=date.today() + timedelta(days=7))
                notes = st.text_area("Notes", height=68)

                if st.form_submit_button("Confirm Borrow", type="primary"):
                    try:
                        borrow_service.borrow_equipment(
                            equipment_id=selected["id"],
                            borrower_name=borrower_name,
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

        # --- Delete Equipment ---
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
