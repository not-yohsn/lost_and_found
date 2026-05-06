# Lost and Found Tracking System

A web-based system for reporting lost items, logging found items, automatically matching them, and notifying owners. Built as the **ITE18** class project.

> Replaces the ad-hoc workflow of Facebook posts and SLG Office logs with a single, centralized platform.

---

## Features

- **Lost reports** with photo, category, location, and date
- **Found items** logged by staff or finders, with photo upload (auto-resized via Pillow)
- **Match engine** — scores candidate pairs by category, shared keywords, and location overlap; shows a *"why this matched"* breakdown
- **Claim workflow** — `pending → approved → released`, with item-status transitions
- **In-app notifications** with unread badge in the navbar (optional email via Flask-Mail)
- **Per-role dashboard** — KPI cards for staff/admin, personal stats for students
- **CSV exports** for lost reports, found items, and claims (staff only)
- **Admin user management** — promote / demote without touching SQL
- **Privacy** — only the reporter and staff see full details on a lost report; other students see item name, photo, category, post date

---

## Tech stack

| Layer        | Choice                                            |
| ------------ | ------------------------------------------------- |
| Backend      | Python 3.12 + Flask 3                             |
| ORM          | SQLAlchemy via Flask-SQLAlchemy                   |
| Auth         | Flask-Login + Werkzeug password hashing           |
| Forms / CSRF | Flask-WTF + WTForms                               |
| Database     | MySQL 8 (XAMPP locally, TiDB Cloud in production) |
| Frontend     | Jinja2 + Bootstrap 5                              |
| Image upload | Pillow                                            |
| Email        | Flask-Mail (optional)                             |
| Production   | Gunicorn on Render                                |

---

## Quick start (local)

### Prerequisites
- Python 3.11+
- XAMPP (for MySQL + phpMyAdmin)
- Git

### Setup
```powershell
git clone https://github.com/<your-user>/lost-and-found.git
cd lost-and-found

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
```

### Database
1. Start MySQL via the XAMPP Control Panel
2. Open http://localhost/phpmyadmin → SQL tab
3. Paste and run [database/schema.sql](database/schema.sql)

### Run
```powershell
python run.py
```

App at **http://127.0.0.1:8000**.

---

## Deploy to Render + TiDB Cloud

1. **TiDB Cloud Serverless** — create a free cluster, run the table-creation statements (without `CREATE DATABASE`/`USE`) in the `test` database
2. **GitHub** — push this repo (GitHub Desktop or `git push`)
3. **Render** — *New + → Web Service* from the repo:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn run:app`
4. **Environment variables** on Render:

   | Key | Value |
   | --- | ----- |
   | `DB_HOST` | TiDB host (ends in `.tidbcloud.com`) |
   | `DB_PORT` | `4000` |
   | `DB_USER` | TiDB user |
   | `DB_PASSWORD` | TiDB password |
   | `DB_NAME` | `test` |
   | `DB_SSL` | `1` |
   | `SECRET_KEY` | output of `python -c "import secrets; print(secrets.token_hex(32))"` |

> **Note:** Render's free tier has an ephemeral filesystem — uploaded photos persist within a deployment but reset on each redeploy. For permanent photos, swap `app/utils.py:save_uploaded_image` to use Cloudinary / S3.

---

## User roles

| Role        | Capabilities                                                                       |
| ----------- | ---------------------------------------------------------------------------------- |
| **Student** | File lost reports, log found items, browse, claim matched items                    |
| **Staff**   | All student capabilities + log office-turned-in items, confirm matches, verify claims, release items |
| **Admin**   | All staff capabilities + manage user roles via `/admin/users`                      |

New accounts always start as **student**. Promote via the admin UI, or directly:

```sql
UPDATE users SET role = 'admin' WHERE email = 'someone@example.com';
```

---

## Project structure

```
.
├── app/
│   ├── __init__.py          # Flask app factory + blueprint registration
│   ├── config.py            # reads .env, handles DB_SSL for cloud MySQL
│   ├── extensions.py        # db, login_manager, mail singletons
│   ├── models.py            # 7 SQLAlchemy entities
│   ├── matching.py          # match scoring (category + keywords + location)
│   ├── notify.py            # in-app + optional email helpers
│   ├── stats.py             # dashboard KPIs
│   ├── decorators.py        # @staff_required / @admin_required
│   ├── utils.py             # image upload + resize
│   ├── auth/                # register / login / logout
│   ├── reports/             # lost reports + CSV export
│   ├── found/               # found items + CSV export
│   ├── matches/             # confirm / dissolve
│   ├── claims/              # claim lifecycle + CSV export
│   ├── notifications/       # inbox + mark-read
│   ├── admin/               # user management
│   ├── main/                # landing page + dashboard
│   ├── templates/           # Jinja2 (Bootstrap 5)
│   └── static/              # CSS + uploaded photos
├── database/
│   └── schema.sql           # MySQL schema for the 7 tables
├── others/                  # original brief + ERD prototype
├── ScopeProject.md          # full scope, milestones, risk register
├── requirements.txt
├── runtime.txt              # Python version pin for Render
├── Procfile                 # Render start command
├── .env.example             # environment template
└── run.py                   # entrypoint
```

---

## Data model

Seven tables, derived from the ERD in [others/prototype.html](others/prototype.html):

`users` · `finders` · `lost_reports` · `found_items` · `matches` · `claims` · `notifications`

See [ScopeProject.md §6](ScopeProject.md) for the full relationship breakdown.

---

## Documentation

See [ScopeProject.md](ScopeProject.md) for project scope, milestones (1 through 8), tools / software inventory, and risk register.

Original brief: [others/LOST-AND-FOUND.pdf](others/LOST-AND-FOUND.pdf).
