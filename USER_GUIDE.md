# Lab Equipment Manager — User Guide

A complete guide for using the Lab Equipment Manager web application.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started — How to Open the Tool](#2-getting-started--how-to-open-the-tool)
3. [Interface Overview](#3-interface-overview)
4. [Using Each Page](#4-using-each-page)
   - 4.1 [Equipment Page](#41-equipment-page-)
   - 4.2 [Borrow & Return Page](#42-borrow--return-page-)
   - 4.3 [Dashboard Page](#43-dashboard-page-)
   - 4.4 [History Page](#44-history-page-)
   - 4.5 [Settings Page](#45-settings-page-️)
5. [Reference](#5-reference)

---

## 1. Introduction

### What is the Lab Equipment Manager?

The **Lab Equipment Manager** is a lightweight web application designed for university engineering laboratories to manage their equipment inventory. It runs in your web browser and requires no installation on individual computers.

### What is it used for?

- **Track equipment** — Know what equipment you have, where it is stored, and how many units are available
- **Manage borrows** — Record who borrowed which equipment, when they borrowed it, and when it is due back
- **Detect overdue items** — Automatically flag equipment that has not been returned by the expected date
- **View history** — Browse a complete timeline of all borrow and return activity
- **Import/export data** — Bulk import equipment from CSV files or export data for backup

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Zero configuration** | Uses SQLite — no database server needed |
| **Single dependency** | Only requires Python and Streamlit |
| **Fast to deploy** | Run locally on any computer with Python installed |
| **Browser-based** | Access through any modern web browser |
| **Simple to use** | Clean interface designed for non-technical users |

---

## 2. Getting Started — How to Open the Tool

### Prerequisites

You need **Python 3.12** or newer installed on your computer.

To check if Python is installed, open a terminal and run:

```bash
python --version
```

If it shows `Python 3.12.x` or higher, you are ready. If not, download and install Python from [python.org](https://www.python.org/downloads/). **Important:** Check the box "Add python.exe to PATH" during installation.

### First-Time Setup

Open a terminal (Command Prompt or PowerShell) and run these commands one by one:

**Step 1:** Navigate to the project folder

```bash
cd "...equipment_manager"
```
In Phat's laptop, that is cd "D:\Project D disk\Tool\equipment_manager"

**Step 2:** Install the required dependency

```bash
pip install -r requirements.txt
```

**Step 3:** Start the application

```bash
python -m streamlit run app.py
```

**Step 4:** Your web browser will automatically open a new tab at `http://localhost:8501`

You should see the Lab Equipment Manager home page.

### Initializing the Database

On your very first run, the database needs to be initialized:

1. Click **⚙️ Settings** in the left sidebar
2. Click the **"Initialize Database"** button
3. You will see a success message: "Database initialized — tables are ready."
4. Click **"Load Sample Data"** to populate the system with 8 example equipment items (optional but recommended for testing)

### Starting the Tool (Subsequent Runs)

After the first-time setup, you only need to run:

```bash
cd "D:\Project D disk\Tool\equipment_manager"
python -m streamlit run app.py
```

Then open your browser to `http://localhost:8501`.

> **Tip:** To stop the application, go back to the terminal and press `Ctrl + C`.

---

## 3. Interface Overview

When you open the application, you will see:

### Sidebar (Left Panel)

The sidebar contains navigation links to all pages:

| Icon | Page | Purpose |
|------|------|---------|
| 🏠 | **Home** | Overview stats and page guide |
| 📦 | **Equipment** | Browse, search, add, borrow, and return equipment |
| 🔄 | **Borrow & Return** | View active borrows and process returns |
| 📊 | **Dashboard** | Statistics and charts |
| 📜 | **History** | Full timeline of all borrow records |
| ⚙️ | **Settings** | Import/export data and manage database |

### Main Content Area

The right side of the screen displays the content of whichever page you have selected.

### Home Page

The home page shows:
- **Quick stats** — Total items, Available, Borrowed, and Maintenance counts
- **Pages table** — A summary of what each page does

---

## 4. Using Each Page

### 4.1 Equipment Page 📦

This is the main page for managing your equipment inventory.

#### Browsing Equipment

When you open the Equipment page, you will see a table listing all equipment with the following columns:

| Column | Description |
|--------|-------------|
| **Asset Code** | Unique identifier (e.g., EQ-001) |
| **Name** | Equipment name (e.g., Oscilloscope) |
| **Category** | Group classification (e.g., Test Equipment, Measurement) |
| **Location** | Storage location (e.g., Lab A, Bench 1) |
| **Status** | Current state: Available, Borrowed, or Maintenance |
| **Condition** | Physical condition: Good, Fair, Poor, or Damaged |
| **Qty** | Number of units |
| **Notes** | Additional information |

#### Filtering Equipment

Use the filter bar at the top of the page to narrow down results:

1. **Search bar** — Type keywords to search by name, asset code, or notes
2. **Category dropdown** — Filter by equipment category (e.g., "Test Equipment")
3. **Status dropdown** — Filter by status (Available, Borrowed, Maintenance)
4. **Location dropdown** — Filter by storage location

All filters work together. For example, selecting category "Measurement" and status "Available" will show only available measurement equipment.

#### Selecting Equipment

Click on any row in the table to select it. An action panel will appear below the table showing:

- Equipment details (asset code, name, status, location, condition)
- Available actions based on the equipment's current status

#### Adding New Equipment

The **"➕ Add New Equipment"** form is always visible at the top of the Equipment page (just below the page title). You do not need to scroll or search for it.

1. Click the **"➕ Add New Equipment"** expander to open the form
2. Fill in the form fields:

| Field | Required? | Description |
|-------|-----------|-------------|
| Asset Code | **Yes** | Unique identifier for the equipment |
| Name | **Yes** | Equipment name |
| Category | No | Group classification (e.g., "Test Equipment") |
| Location | No | Where it is stored (e.g., "Lab A, Bench 1") |
| Status | No | Defaults to "Available" |
| Condition | No | Defaults to "Good" |
| Quantity | No | Defaults to 1 |
| Notes | No | Any additional details |

3. Click **"Add Equipment"**
4. A success message confirms the equipment was added

> **Note:** Asset codes must be unique. If you try to add equipment with an existing asset code, you will see an error.

> **Tip:** The "Add New Equipment" form is always visible at the top of the Equipment page, even when the equipment list is empty. This is the first thing you will see after navigating to the page.

#### Borrowing Equipment from This Page

1. Click on an **Available** item in the table
2. A borrow form will appear below the table
3. Fill in:
   - **Borrower Name** (required) — Name of the person borrowing the equipment
   - **Borrow Date** — Defaults to today
   - **Expected Return Date** — Defaults to 7 days from today
   - **Notes** (optional) — Any additional information
4. Click **"Confirm Borrow"**
5. The equipment status automatically changes to "Borrowed"

#### Returning Equipment from This Page

1. Click on a **Borrowed** item in the table
2. You will see information about who currently has the equipment
3. Click **"Return Equipment"**
4. The equipment status automatically changes back to "Available"

#### Maintenance Items

If an item is marked as **Maintenance**, no borrow or return actions are available. You will see a warning message. To make it available again, you must update its status through the database or re-add it.

#### Deleting Equipment

You can permanently delete equipment from the system. **Borrow history records are preserved** — the asset code and equipment name are saved in each borrow record at the time of borrowing, so your history remains complete even after the equipment is deleted.

**Steps:**

1. Click on the equipment row you want to delete in the table
2. Scroll down to the **"Delete [Asset Code]"** section in the action panel
3. If the equipment has **active borrows**, you will see a warning: "Cannot delete — this equipment has active borrows. Return it first." You must return the equipment before deleting it.
4. If there are no active borrows, you will see an info message: "Borrow history for this equipment will be preserved after deletion."
5. Check the box **"I confirm I want to delete this equipment permanently"**
6. Click **"Delete Equipment"**
7. A success message confirms the deletion

> **Note:** After deletion, the equipment will no longer appear in the Equipment list or be available for borrowing. However, all past borrow records remain in the History page with the original asset code and equipment name intact.

---

### 4.2 Borrow & Return Page 🔄

This page provides a dedicated view for managing all active borrows.

#### Active Borrows Table

The top section shows a table of all currently borrowed equipment:

| Column | Description |
|--------|-------------|
| **Asset Code** | Equipment identifier |
| **Equipment** | Equipment name |
| **Borrower** | Person who borrowed it |
| **Since** | Date when it was borrowed |
| **Due** | Expected return date |
| **Overdue** | Shows "⚠ Overdue" if past due date |

If any items are overdue, a warning banner appears at the top: **"X item(s) overdue — return requested!"**

#### Returning Equipment

1. Scroll to the **"📥 Return Equipment"** section
2. Use the dropdown to select the item you want to return (shows asset code, name, and borrower)
3. Click **"Return Equipment"**
4. A success message confirms the return

#### Borrowing Equipment

1. Scroll to the **"📦 Borrow Equipment"** section
2. Fill in the form:
   - **Equipment** (required) — Select from the dropdown list of available items
   - **Borrower Name** (required) — Enter the borrower's name
   - **Borrow Date** — Defaults to today
   - **Expected Return Date** — Defaults to 7 days from today
   - **Notes** (optional) — Any additional information
3. Click **"Confirm Borrow"**
4. A success message confirms the borrow

> **Note:** Only equipment with status "Available" will appear in the dropdown. If no equipment is available, you will see the message "No equipment currently available to borrow."

---

### 4.3 Dashboard Page 📊

The dashboard provides a visual overview of your equipment inventory and recent activity.

#### Summary Cards

Four metric cards at the top show:

| Card | Description |
|------|-------------|
| **Total Items** | Total number of equipment items in the system |
| **Available** | Items with status "Available" |
| **Borrowed** | Items currently borrowed |
| **Maintenance** | Items under maintenance |

#### Overdue Warning

If any items are overdue, a yellow warning banner appears: **"⚠ X item(s) overdue — return requested!"**

#### Charts

Two bar charts display:

1. **Equipment by Category** — Shows how many items exist in each category (e.g., Test Equipment: 3, Measurement: 2)
2. **Equipment by Location** — Shows how many items are stored in each location (e.g., Lab A: 5, Lab B: 3)

#### Recent Borrow Activity

A table showing the 10 most recent borrow records with columns:

| Column | Description |
|--------|-------------|
| **Asset Code** | Equipment identifier |
| **Equipment** | Equipment name |
| **Borrower** | Person who borrowed it |
| **Borrowed** | Date borrowed |
| **Due** | Expected return date |
| **Returned** | Actual return date (or "—" if not yet returned) |
| **Status** | Active, Returned, or Overdue |

---

### 4.4 History Page 📜

This page displays a complete timeline of all borrow records, organized by month.

#### Timeline View

Records are grouped by month in expandable sections. Each section shows the month name and number of records (e.g., "📅 July 2026 — 3 record(s)").

- The current month's section is expanded by default
- Other months are collapsed — click to expand

Each record in the timeline shows:

- **Date and equipment** — e.g., "**2026-07-15** — `EQ-001` Oscilloscope"
- **Borrower and status** — e.g., "Borrowed by **John** | Due 2026-07-22 — 🔵 Active"
- **Notes** — If any notes were recorded, they appear below

#### Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| 🔵 | Active | Currently borrowed, not yet due |
| ✅ | Returned | Already returned |
| ⚠ | Overdue | Past the expected return date, not yet returned |

#### Search

Use the search bar to find records by:
- Borrower name
- Equipment name
- Asset code

The search is case-insensitive and matches partial text.

#### Filters

1. **Status filter** — Show only Active, Returned, or Overdue records
2. **Borrower filter** — Show only records from a specific borrower (dropdown auto-populated from existing data)

Filters work together with the search bar. You can combine all three to narrow down results.

---

### 4.5 Settings Page ⚙️

This page manages data import/export and database operations.

#### 📥 Import Equipment from CSV

Bulk import equipment from a CSV file.

**Steps:**

1. Click **"Browse files"** or drag and drop a CSV file
2. The system will:
   - Validate the file encoding (must be UTF-8)
   - Check that required columns exist (`asset_code`, `name`)
   - Show a preview of the first 5 rows
3. Review the preview to confirm the data looks correct
4. Click **"Import X record(s)"** to proceed
5. Results will show:
   - Number of items successfully imported
   - Any rows that were skipped (with error reasons)

**CSV Format Requirements:**

| Column | Required? | Valid Values |
|--------|-----------|--------------|
| `asset_code` | **Yes** | Any unique text (e.g., "EQ-001") |
| `name` | **Yes** | Any text |
| `category` | No | Any text (e.g., "Test Equipment") |
| `location` | No | Any text (e.g., "Lab A, Bench 1") |
| `status` | No | "Available", "Borrowed", or "Maintenance" |
| `condition` | No | "Good", "Fair", "Poor", or "Damaged" |
| `quantity` | No | Any positive integer (defaults to 1) |
| `notes` | No | Any text |

**Example CSV file:**

```csv
asset_code,name,category,location,status,condition,quantity,notes
EQ-001,Oscilloscope,Test Equipment,Lab A,Available,Good,2,Keysight DSOX1202G
EQ-002,Multimeter,Measurement,Lab B,Available,Good,4,Fluke 87V
EQ-003,Function Generator,Test Equipment,Lab A,Available,Good,1,Siglent SDG1032X
```

> **Tip:** You can export your current data first (see below), then edit the CSV to use as a template.

#### 📤 Export Equipment to CSV

Download all equipment data as a CSV file for backup or editing.

1. Click the **"Download equipment_export.csv (X records)"** button
2. A CSV file will be downloaded to your computer
3. The file contains all equipment fields and can be re-imported later

#### 🗄️ Database

| Button | Description |
|--------|-------------|
| **Initialize Database** | Creates the database tables if they don't exist. Also runs automatic schema migrations if needed. Safe to run multiple times. |
| **Load Sample Data** | Adds 8 example equipment items for testing. Skips items with duplicate asset codes. |

> **Note:** If you are upgrading from an older version, clicking "Initialize Database" will automatically migrate your existing data to the new schema. No data is lost.

#### ⚠️ Reset Database — Danger Zone

> **Warning:** This permanently deletes ALL equipment and borrow history records. This action cannot be undone.

1. Click **"⚠️ Reset Database — Danger Zone"** to expand the section
2. Read the warning carefully
3. **Recommended:** Export your data to CSV first
4. Click **"Confirm Reset — Delete All Data"**
5. All data will be deleted

---

## 5. Reference

### Asset Code Convention

Asset codes are unique identifiers for each equipment item. There is no enforced format in the system, but for multi-discipline labs, we recommend the following convention:

**Format:** `[Prefix]-[Number]`

| Field | Prefix | Examples |
|-------|--------|----------|
| Electrical | `EL-` | `EL-001`, `EL-002`, `EL-003` |
| Mechanical | `MC-` | `MC-001`, `MC-002` |
| Chemical | `CH-` | `CH-001`, `CH-002` |
| General / Other | `GN-` | `GN-001`, `GN-002` |

**Tips:**

- Keep prefixes short (2–3 letters)
- Use sequential numbering (`001`, `002`, `003`...)
- Be consistent — pick one format and stick with it across the entire lab
- Asset codes must be **unique** — no two equipment items can share the same code

**Example — Electrical lab inventory:**

| Asset Code | Name | Location |
|------------|------|----------|
| EL-001 | Oscilloscope | Lab A, Bench 1 |
| EL-002 | Digital Multimeter | Lab A, Bench 2 |
| EL-003 | Function Generator | Lab A, Bench 1 |
| EL-004 | DC Power Supply | Lab B, Bench 1 |
| MC-001 | 3D Printer | Lab C, Bench 1 |
| CH-001 | Chemical Fume Hood | Lab D, Room 2 |

### Category Convention

Categories help group equipment by type for easier filtering and browsing. There is no enforced format in the system, but we recommend the following categories:

| Category | What Goes Here |
|----------|----------------|
| Test Equipment | Oscilloscopes, logic analyzers, signal generators |
| Measurement | Multimeters, LCR meters, calipers, scales |
| Power | DC power supplies, AC sources, battery packs |
| Tools | Soldering stations, wire strippers, crimpers |
| Components | Breadboards, jumper wires, kits |
| Safety | Fire extinguishers, goggles, first aid kits |
| Fabrication | 3D printers, CNC machines, laser cutters |
| Chemical | Beakers, flasks, fume hoods, titration equipment |
| Mechanical | Wrenches, torque drivers, clamps |
| Miscellaneous | Items that don't fit other categories |

**Tips:**

- Keep categories short (1–2 words)
- Use Title Case (`Test Equipment`, not `test equipment`)
- Be consistent — pick one name and stick with it
- You can add new categories anytime as your inventory grows

### Equipment Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | Integer | Auto | — | Unique identifier (auto-generated) |
| `asset_code` | Text | **Yes** | — | Unique equipment identifier |
| `name` | Text | **Yes** | — | Equipment name |
| `category` | Text | No | `""` | Group classification |
| `location` | Text | No | `""` | Storage location |
| `status` | Text | No | `"Available"` | Current status |
| `condition` | Text | No | `"Good"` | Physical condition |
| `quantity` | Integer | No | `1` | Number of units (min: 1) |
| `notes` | Text | No | `""` | Additional information |
| `created_at` | Timestamp | Auto | Current time | When the record was created |
| `updated_at` | Timestamp | Auto | Current time | When the record was last updated |

### Valid Status Values

| Status | Meaning |
|--------|---------|
| `Available` | Equipment is in storage and can be borrowed |
| `Borrowed` | Equipment is currently loaned out |
| `Maintenance` | Equipment is being serviced or repaired |

### Valid Condition Values

| Condition | Meaning |
|-----------|---------|
| `Good` | Equipment is in working order |
| `Fair` | Equipment shows minor wear but is functional |
| `Poor` | Equipment has significant wear or minor issues |
| `Damaged` | Equipment is broken or non-functional |

### Borrow Record Status Logic

The status of a borrow record is automatically determined:

1. If `actual_return_date` is set → **"Returned"**
2. Else if `expected_return_date` < today → **"Overdue"**
3. Else → **"Active"`

### Borrow History Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique record identifier (auto-generated) |
| `equipment_id` | Integer | Reference to the equipment item |
| `borrower_name` | Text | Name of the person who borrowed the item |
| `borrow_date` | Text | Date the item was borrowed (YYYY-MM-DD) |
| `expected_return_date` | Text | Date the item is expected back (YYYY-MM-DD) |
| `actual_return_date` | Text | Date the item was actually returned (NULL if not yet returned) |
| `notes` | Text | Any additional notes about the borrow |
| `created_at` | Timestamp | When the record was created |

---

*This guide covers version 1.0 of the Lab Equipment Manager.*
