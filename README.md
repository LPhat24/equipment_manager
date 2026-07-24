# Lab Equipment Manager

A lightweight internal web application for managing laboratory equipment inventory.

Built for university engineering labs — simple, fast, and easy to maintain.

---

## For Users

> **No setup required.** Access the tool directly in your browser:

**https://fm-src-feet.streamlit.app/**

- Works on any device with a web browser (computer, tablet, or mobile phone)
- No installation needed — just open the URL
- All data is stored in the cloud — shared across all users

---

## Development Stages

```
Version 1.0 — Completed
+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Requirement |  Analysis   |    Design   | Build Tests | Development |   Testing   |   Confirm   |
+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
                                                            [COMPLETE]      [COMPLETE]     [COMPLETE]

Version 2.0 — In Progress
+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
| Requirement |  Analysis   |    Design   | Build Tests | Development |   Testing   |   Confirm   |
+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
                                                                      >>> [CURRENT] <<<
```

---

## Version History

### Version 1.0 — Terminal-only, Local Database

| Feature | Description |
|---------|-------------|
| Database | SQLite (local file, single-machine) |
| Equipment Management | Add, browse, search, filter by category/status/location |
| Borrow & Return | Single-item borrow and return with automatic status tracking |
| Dashboard | Stats cards, category/location charts, recent activity |
| Borrow History | Timeline of all records with search and filters |
| Settings | CSV import/export, sample data, database init |
| Access | Terminal only — `streamlit run App.py` on local machine |
| Deployment | None — runs locally |

### Version 2.0 — Cloud-deployed, PostgreSQL

| Feature | Description |
|---------|-------------|
| Database | PostgreSQL (Neon serverless) — shared across users/machines |
| Cloud Deployment | Streamlit Community Cloud — accessible via browser URL |
| Borrower Phone | Phone number tracking for all borrows |
| Overdue Detection | Automatic flagging + dedicated Overdue contact list page |
| Multi-Select Filters | Category, Status, Location — OR logic within each filter |
| Quantity-Based Borrowing | Borrow partial copies from multi-copy items |
| Per-Item Bulk Borrow | Set individual quantities per item in bulk borrow |
| Bulk Return | Multi-select return with filters (borrower/category/location) |
| Borrower Notes | Notes visible in Dashboard, Borrow & Return, Equipment |
| Input Validation | Name ≥ 2 chars, Phone ≥ 8 digits, 90-day max borrow |
| Form Retention | Form data kept on validation errors |
| Connection Pooling | Reused PostgreSQL connections for faster page loads |
| Full-Width Layout | Wider content area for better readability |

---

## Features

- **Equipment Management** — Add, browse, search, filter equipment by category/status/location (multi-select with OR logic)
- **Borrow & Return** — One-click borrow and return with automatic status tracking, quantity-based borrowing
- **Bulk Operations** — Bulk borrow with per-item quantity, bulk return with filters
- **Overdue Detection** — Items past their return date are automatically flagged
- **Dashboard** — Quick stats, category/location charts, recent activity with borrower notes
- **Borrow History** — Full timeline of all borrow records with search and filters
- **CSV Import/Export** — Bulk import equipment from CSV, export data for backup
- **Sample Data** — Load demo equipment for quick testing

## Tech Stack

- **Frontend:** Streamlit
- **Database:** PostgreSQL (Neon serverless) with connection pooling
- **Language:** Python 3.12+
- **Dependencies:** Streamlit, psycopg2, python-dotenv

## Setup

> **Note: This section is for developers only.** If you just want to use the tool, see [For Users](#for-users) above.

```bash
git clone https://github.com/LPhat24/equipment_manager.git
```

After cloning, open the `equipment_manager` folder on your computer, then open Terminal (or Command Prompt) in that folder and run:

```bash
pip install -r requirements.txt
python -m streamlit run App.py
```

The app opens at `http://localhost:8501`.

On first run, go to **⚙️ Settings** and click **Initialize Database**, then **Load Sample Data**.

---

## For Contributors

> **Access Policy:** Source code files (Python, configuration) are restricted to the
> project owner (Le Thanh Phat). Contributors may only work with the **TESTING/**
> folder for test case creation and execution.

### Clone the Repository

```bash
git clone https://github.com/LPhat24/equipment_manager.git
```

After cloning, open the `equipment_manager` folder on your computer, then open Terminal (or Command Prompt) in that folder.

### Your Workspace — TESTING/ Folder

Only the `TESTING/` folder is accessible for contributor work:

```
TESTING/
├── TEST_CASES.csv                                                      # Editable copy (you modify this)
└── Lab Equipment Manager - Test Cases - TEST_CASES.csv                 # Google Sheets export (read-only reference)
```

### How Test Cases Work

1. **Export from Google Sheets** → Download the test case sheet as CSV
2. **Overwrite** → Replace `Lab Equipment Manager - Test Cases - TEST_CASES.csv` in the `TESTING/` folder with the exported file
3. **Using AI to build Test Cases** → Instruct the AI to read `Lab Equipment Manager - Test Cases - TEST_CASES.csv` to understand the current Test Case Sheet context
4. **Modifications or Upgrades** → Edit `TEST_CASES.csv` (the working copy)
5. **Import back to Google Sheets** → Use `TEST_CASES.csv` to replace the old sheet in Google Sheets
6. **Testing must follow ISTQB standards**

### Edit Test Cases

- Open `TESTING/TEST_CASES.csv` in any text editor or spreadsheet tool
- Each row is a test case with columns: TC_ID, Feature, Title, Priority, Preconditions, Test_Steps, Test_Data, Expected_Result, Actual_Result, Status, Tester, Date_Executed, Notes, Build_Version
- Fill in Actual_Result, Status, Tester, Date_Executed after executing tests

### Push Your Work

```bash
git add TESTING/
git commit -m "test: update test cases for TC-XXX"
git push
```

### Pull Latest Changes

```bash
git pull
```

---

## Project Structure

> **Note: This section is for developers only.**

```
equipment_manager/
├── App.py                          # Main entry point (lowercase on Streamlit Cloud)
├── pages/                          # Streamlit multipage navigation
│   ├── Equipment.py                # Browse, search, filter, add, borrow, return
│   ├── Borrow_Return.py            # Active borrows, bulk return with filters
│   ├── Dashboard.py                # Stats cards, charts, recent activity
│   ├── History.py                  # Timeline of all borrow records
│   ├── Overdue.py                  # Overdue items + borrower contact list
│   └── Settings.py                 # CSV import/export, database management
├── services/                       # Business logic layer
│   ├── equipment_service.py        # Equipment validation and CRUD
│   ├── borrow_service.py           # Borrow/return workflow with transactions
│   └── history_service.py          # History queries and statistics
├── database/                       # Data access layer
│   ├── schema.py                   # Table definitions and connection management
│   ├── db.py                       # Connection pooling and generic CRUD utilities
│   ├── equipment_repo.py           # Equipment SQL queries
│   └── borrow_repo.py              # Borrow history SQL queries
├── utils/
│   ├── helpers.py                  # Shared utility functions
│   └── styling.py                  # Full-width CSS injection
├── scripts/
│   └── migrate_sqlite_to_pg.py     # One-time SQLite → PostgreSQL migration
├── TESTING/                        # Test cases (contributors work here)
│   ├── TEST_CASES.csv              # Editable test case file
│   └── Lab Equipment Manager - Test Cases - TEST_CASES.csv
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── USER_GUIDE.md                   # End-user guide
├── .env.example                    # DATABASE_URL template
├── .gitignore                      # Git ignore rules
└── .streamlit/secrets.toml         # Streamlit secrets (not in Git)
```

## Architecture

> **Note: This section is for developers only.**

```
Presentation Layer (pages/)    →  Streamlit UI only
        ↓
Business Layer (services/)     →  Validation, workflows, rules
        ↓
Data Layer (database/)         →  SQL queries, CRUD, connection management
        ↓
PostgreSQL (Neon serverless)    →  Cloud-hosted, shared across users
```

- Pages only communicate with services
- Services only communicate with repos
- Repos only communicate with db.py utilities
- Each layer has a single responsibility

---

## CSV Import Format

> **Note: This section is for developers only.**

When importing equipment via **⚙️ Settings**, use this CSV format:

```csv
asset_code,name,category,location,status,condition,quantity,notes
EQ-001,Oscilloscope,Test Equipment,Lab A,Available,Good,2,Keysight DSOX1202G
EQ-002,Multimeter,Measurement,Lab B,Available,Good,4,Fluke 87V
```

**Required columns:** `asset_code`, `name`

**Optional columns:** `category`, `location`, `status`, `condition`, `quantity`, `notes`

**Valid values:**
- `status`: Available, Borrowed, Maintenance
- `condition`: Good, Fair, Poor, Damaged

---

## License

Internal use only.
