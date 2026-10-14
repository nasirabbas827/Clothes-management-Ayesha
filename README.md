# Clothes Management Ayesha

Clothes-management-Ayesha is a desktop application for clothing inventory, purchases, and sales.

![Tkinter](https://img.shields.io/badge/Tkinter-2563EB?style=flat-square) ![SQLite](https://img.shields.io/badge/SQLite-0F172A?style=flat-square)

## Overview

The Tkinter implementation is organized around the entry points and modules below.

## Modules

- [`src/admin_dashboard.py`](src/admin_dashboard.py) — Admin Dashboard
- [`src/admin_purchase.py`](src/admin_purchase.py) — Admin Purchase
- [`src/app.py`](src/app.py) — App
- [`src/database.py`](src/database.py) — Database
- [`src/login.py`](src/login.py) — Login
- [`src/manage_items.py`](src/manage_items.py) — Manage Items
- [`src/manage_users.py`](src/manage_users.py) — Manage Users
- [`src/reports.py`](src/reports.py) — Reports
- [`src/user_dashboard.py`](src/user_dashboard.py) — User Dashboard
- [`src/user_items.py`](src/user_items.py) — User Items

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/Clothes-management-Ayesha.git
cd Clothes-management-Ayesha
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install Pillow tkcalendar
```

Dependency versions are not pinned in this repository.

A working Tkinter installation and a graphical desktop session are required.

### 3. Configure and run

Keep the included SQLite database files in their expected locations: [`clothes_db.db`](clothes_db.db).

Run from the repository root so relative file paths resolve correctly:

```bash
python src/app.py
```

## Repository guide

| Path | Purpose |
| --- | --- |
| [`src`](src) | Desktop application source modules |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
