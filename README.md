# Lab Equipment Manager

A lightweight internal web application for managing laboratory equipment inventory.

Built for university engineering labs — simple, fast, and easy to maintain.

## Features

- **Equipment Management** — Add, browse, search, filter equipment by category/status/location
- **Borrow & Return** — One-click borrow and return with automatic status tracking
- **Overdue Detection** — Items past their return date are automatically flagged
- **Dashboard** — Quick stats, category/location charts, recent activity
- **Borrow History** — Full timeline of all borrow records with search and filters
- **CSV Import/Export** — Bulk import equipment from CSV, export data for backup
- **Sample Data** — Load demo equipment for quick testing

## Tech Stack

- **Frontend:** Streamlit
- **Database:** SQLite (zero configuration)
- **Language:** Python 3.12+
- **Dependencies:** Streamlit only (SQLite is in Python stdlib)

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd equipment_manager

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app opens at `http://localhost:8501`.

On first run, go to **⚙️ Settings** and click **Initialize Database**, then **Load Sample Data**.

## Project Structure

```
equipment_manager/
├── app.py                      # Main entry point
├── pages/                      # Streamlit multipage navigation
│   ├── Equipment.py            # Browse, search, filter, add, borrow, return
│   ├── Borrow_Return.py        # Active borrows, quick return, borrow form
│   ├── Dashboard.py            # Stats cards, charts, recent activity
│   ├── History.py              # Timeline of all borrow records
│   └── Settings.py             # CSV import/export, database management
├── services/                   # Business logic layer
│   ├── equipment_service.py    # Equipment validation and CRUD
│   ├── borrow_service.py       # Borrow/return workflow with transactions
│   └── history_service.py      # History queries and statistics
├── database/                   # Data access layer
│   ├── schema.py               # Table definitions and connection management
│   ├── db.py                   # Generic CRUD utilities and context manager
│   ├── equipment_repo.py       # Equipment SQL queries
│   └── borrow_repo.py          # Borrow history SQL queries
├── utils/
│   └── helpers.py              # Shared utility functions
├── assets/                     # Static assets (reserved for future use)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .gitignore                  # Git ignore rules
```

## Architecture

```
Presentation Layer (pages/)    →  Streamlit UI only
        ↓
Business Layer (services/)     →  Validation, workflows, rules
        ↓
Data Layer (database/)         →  SQL queries, CRUD, connection management
        ↓
SQLite (database/database.db)  →  File-based storage
```

- Pages only communicate with services
- Services only communicate with repos
- Repos only communicate with db.py utilities
- Each layer has a single responsibility

## CSV Import Format

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

## License

Internal use only.
