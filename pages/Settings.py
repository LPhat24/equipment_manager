import streamlit as st
import csv
import io

from database.schema import init_db
from services import equipment_service
from utils.styling import apply_full_width

DB_PASSWORD = "admin123"

apply_full_width()

st.title("⚙️ Settings")

# --- CSV Import ---
st.subheader("📥 Import Equipment from CSV")

st.markdown(
    "Upload a CSV file with columns: `asset_code`, `name` (required), "
    "plus optional `category`, `location`, `status`, `condition`, `quantity`, `notes`."
)

uploaded = st.file_uploader("Upload CSV file", type=["csv"], label_visibility="collapsed")

if uploaded:
    try:
        content = uploaded.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
    except UnicodeDecodeError:
        st.error("File encoding not supported. Please save the CSV as UTF-8.")
        st.stop()

    if not reader.fieldnames:
        st.error("CSV file is empty or has no headers.")
        st.stop()

    required_cols = {"asset_code", "name"}
    actual_cols = set(reader.fieldnames)
    missing = required_cols - actual_cols

    if missing:
        st.error(f"Missing required columns: {', '.join(sorted(missing))}")
        st.stop()

    rows = list(reader)

    if not rows:
        st.warning("CSV file contains headers but no data rows.")
        st.stop()

    st.info(f"**{len(rows)}** record(s) found in file. Preview:")

    display_rows = [{k: row.get(k, "") for k in reader.fieldnames} for row in rows[:5]]
    st.dataframe(display_rows, use_container_width=True, hide_index=True)

    if len(rows) > 5:
        st.caption(f"Showing 5 of {len(rows)} rows.")

    if st.button(f"Import {len(rows)} record(s)", type="primary"):
        inserted = 0
        errors = []

        for i, row in enumerate(rows, 1):
            try:
                equipment_service.add_equipment(row)
                inserted += 1
            except ValueError as e:
                errors.append(f"Row {i} ({row.get('asset_code', '?')}): {e}")

        if inserted > 0:
            st.success(f"Successfully imported **{inserted}** equipment item(s).")
        if errors:
            st.warning(f"**{len(errors)}** row(s) skipped:")
            for err in errors:
                st.text(f"  ✗ {err}")

st.markdown("---")

# --- CSV Export ---
st.subheader("📤 Export Equipment to CSV")

all_items = equipment_service.get_all_equipment()

if not all_items:
    st.info("No equipment to export.")
else:
    st.info(f"**{len(all_items)}** equipment record(s) ready for export.")

    export_cols = ["asset_code", "name", "category", "location", "status", "condition", "quantity", "notes"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=export_cols)
    writer.writeheader()

    for item in all_items:
        writer.writerow({k: item[k] for k in export_cols})

    csv_data = output.getvalue()

    st.download_button(
        label=f"Download equipment_export.csv ({len(all_items)} records)",
        data=csv_data,
        file_name="equipment_export.csv",
        mime="text/csv",
        type="primary",
    )

st.markdown("---")

# --- Database ---
st.subheader("🗄️ Database")

if "db_password_ok" not in st.session_state:
    st.session_state["db_password_ok"] = False

if not st.session_state["db_password_ok"]:
    pwd_col1, pwd_col2 = st.columns([3, 1])
    with pwd_col1:
        db_password_input = st.text_input("Enter password to access database operations", type="password")
    with pwd_col2:
        st.write("")
        st.write("")
        if st.button("Verify", use_container_width=True):
            if db_password_input == DB_PASSWORD:
                st.session_state["db_password_ok"] = True
                st.rerun()
            else:
                st.error("Wrong password")
else:
    st.success("Password verified")

    db_col1, db_col2 = st.columns(2)

    with db_col1:
        if st.button("Initialize Database", use_container_width=True):
            try:
                init_db()
                st.success("Database initialized — tables are ready.")
            except Exception as e:
                st.error(f"Initialization failed: {e}")

    with db_col2:
        if st.button("Load Sample Data", use_container_width=True):
            inserted, errors = equipment_service.load_sample_data()
            if inserted > 0:
                st.success(f"Loaded **{inserted}** sample equipment item(s).")
            if errors:
                for err in errors:
                    st.text(f"  ✗ {err}")

    st.markdown("---")

    # --- Danger Zone ---
    with st.expander("⚠️ Reset Database — Danger Zone"):
        st.warning(
            "This will **permanently delete** ALL equipment and borrow history records. "
            "This action cannot be undone."
        )
        st.caption("Tip: Export your data to CSV first before resetting.")

        reset_confirm = st.checkbox("I confirm I want to delete ALL data permanently")
        if st.button("Confirm Reset — Delete All Data", type="primary", disabled=not reset_confirm):
            try:
                equipment_service.reset_all_data()
                st.success("All data has been deleted.")
            except Exception as e:
                st.error(f"Reset failed: {e}")
