# Lost & Found Tracking System — Presentation Notes

A reference for the class demo: background, tech stack, user manual, and likely Q&A.

---

## 1. System Background

**Problem statement** (from the brief):
- Lost items are scattered across Facebook groups, posted ad hoc, with no central record
- Reports go to the **Student Local Government Office** in person, where they may be lost or mis-recorded
- Returning items is delayed because nobody can quickly cross-reference what's been lost vs. what's been turned in

**Proposed solution** — a centralized web app where:

1. Students **report lost items** (description, photo, location, date)
2. Staff and finders **log found items** the same way
3. A **match engine** automatically suggests likely pairs
4. Owners get **notified** when their item appears
5. A **claim workflow** verifies ownership before staff releases the item
6. All records persist, all status changes are tracked

---

## 2. Tech Stack

| Layer | Choice | Why |
| ----- | ------ | --- |
| Backend | **Python 3.11 + Flask 3** | Lightweight, fast to develop, huge ecosystem |
| Templating | **Jinja2** (bundled with Flask) | Server-side rendering, no SPA complexity |
| ORM | **SQLAlchemy 2 / Flask-SQLAlchemy** | DB-agnostic — same code runs on SQLite + MySQL |
| Auth | **Flask-Login + Werkzeug** | Session-based; passwords stored as PBKDF2-SHA256 hashes |
| Forms / CSRF | **Flask-WTF + WTForms** | Built-in CSRF tokens, server-side validation |
| Database | **SQLite** (production), **MySQL** (local dev) | SQLite is file-based & free on PA's free tier |
| Frontend | **Bootstrap 5 + vanilla JS** | Responsive, no build step needed |
| Image upload | **Pillow** | Resize to 1200px max, JPEG quality 85 (~80% smaller files) |
| Email | **Flask-Mail** *(optional)* | Skipped on free tier; in-app notifications fill in |
| Hosting | **PythonAnywhere** (free Beginner plan) | Built for Python; SQLite + venv supported on free tier |
| Source control | **Git + GitHub** | Standard, deploys via `git pull` on PA |

**Architecture pattern:** Flask **application factory** + **blueprints** — eight feature modules (`auth`, `reports`, `found`, `matches`, `claims`, `notifications`, `admin`, `main`), each with its own routes, forms, and templates.

---

## 3. User's Manual

### 3.1 Roles

| Role | What they can do |
| ---- | ---------------- |
| **Student** | Register, file lost reports, browse found items, claim matched items |
| **Staff** | Everything a student can + log found items at the office, confirm matches, verify claims, release items |
| **Admin** | Everything staff can + promote/demote users via the Users page |

New accounts always default to **student**. Staff/admin promotion is done by an existing admin (or via SQL on first setup).

### 3.2 Student workflow

1. **Register** at `/auth/register` → log in
2. From dashboard → **Report a lost item**
3. Fill the form (item name, description, photo, location, date) → submit
4. On the detail page, see **"Possible matches"** if any found items overlap (only visible to you + staff)
5. When staff confirms a match, you receive a notification (bell icon turns red)
6. Click the notification → **Claim this item** → add proof-of-ownership notes
7. Wait for staff approval → visit the office → staff releases the item
8. Final notification: **"Item released"** → your report is now **Closed**

### 3.3 Staff workflow

1. Log in → staff dashboard shows: pending claims, active lost reports, items in custody, match rate
2. **Log a found item** when someone hands it in
3. On any report/item detail, click **Confirm match** under "Possible matches" to link a pair
4. **Claims** tab → review pending claims → **Approve** or **Reject**
5. After approval, when the student picks up the item → click **Mark as released**
6. Use **CSV exports** for periodic reporting

### 3.4 Admin workflow

Same as staff, plus:
- **Users** page (`/admin/users`) — change anyone's role with a dropdown
- Self-demotion is blocked (so you can't lock yourself out)

### 3.5 Privacy

Other students who browse a lost report see only: **item name, photo, category, post date, status**. The description, exact location, date lost, and reporter name are visible only to the reporter and to staff/admin. A small notice on the page explains this.

---

## 4. Likely Technical Questions (with answers)

### 4.1 — Why Flask over Django?
Flask's lighter footprint matches a single-team class project. Django's batteries-included features (admin, ORM, auth) would have been overkill; we got the same result with smaller Flask extensions.

### 4.2 — Why SQLite in production instead of MySQL?
PythonAnywhere's free tier no longer includes MySQL. SQLAlchemy abstracts the dialect, so the *same models* work on either. SQLite is single-file, has no separate server, and is fine for the expected scale (a school's volume of lost items).

### 4.3 — How does the match engine work?
A pure-Python scoring function in `app/matching.py`. Each lost-report ↔ found-item pair gets:

- **+0.4** if categories match exactly
- **+0.1** per shared keyword (cap +0.4) — tokenized lowercase alphanumeric ≥3 chars, stopwords removed
- **+0.2** if any shared word in the location fields

A date filter discards found items dated before *lost_date − 1 day*. Candidates with score ≥ 0.2 appear as suggestions; ≥ 0.3 triggers a notification.

### 4.4 — How are passwords stored?
Hashed with Werkzeug's `generate_password_hash`, which uses PBKDF2-SHA256 with random salts. Plaintext passwords are never written to the DB or logs.

### 4.5 — How is CSRF prevented?
Every form uses Flask-WTF's `FlaskForm`. The `{{ form.hidden_tag() }}` template call inserts a per-session CSRF token; the framework validates it on POST. State-changing requests fail without it.

### 4.6 — How is role-based access enforced?
Two decorators in `app/decorators.py` — `@staff_required` and `@admin_required` — check `current_user.role` and call `abort(403)` if unauthorized. Plus per-route ownership checks (e.g., only the lost-report owner can submit a claim).

### 4.7 — What's the data model?
Seven tables: `users`, `finders`, `lost_reports`, `found_items`, `matches`, `claims`, `notifications`. The ERD is at `others/prototype.html`. Key relationships:

- `users` 1—N `lost_reports`
- `lost_reports` 1—1 `matches` ↔ `found_items`
- `matches` 1—N `claims`

Status transitions are managed in route handlers (e.g., releasing a claim sets the lost report to `closed` and the found item to `released`).

### 4.8 — How are uploaded photos handled?
`app/utils.py:save_uploaded_image` validates extension, uses Pillow to thumbnail to max 1200 px, saves as JPEG q=85 with a UUID filename. Max file size 3 MB, enforced by `MAX_CONTENT_LENGTH`.

### 4.9 — Why blueprints instead of one big `routes.py`?
Each feature has its own blueprint so the code stays modular. URL prefixes (`/auth/...`, `/reports/...`, etc.) come from registration in `app/__init__.py`, not hard-coded paths.

### 4.10 — How would you scale this beyond one school?
- Switch the SQLite file to a managed Postgres or MySQL
- Move uploads from local disk to S3 / Cloudinary
- Replace the simple matching loop with full-text search or vector-embedding fuzzy matching
- Add Celery for async notifications and image processing
- Front the app with nginx + multiple Gunicorn workers

### 4.11 — Why is the chatbot not part of this app?
Out of scope. The chatbot prototype in `others/` describes a separate customer-service concept; integrating it would be a v2 feature.

### 4.12 — How would you test this?
Pytest with Flask's test client — create test users, file reports, confirm matches, assert status transitions and that the right notifications fire. SQLAlchemy makes it easy to use a separate in-memory SQLite DB per test.

### 4.13 — What's the deployment flow?
1. Local edit → commit → `git push`
2. SSH into PythonAnywhere
3. `git pull origin main` → if deps changed, `pip install -r requirements.txt`
4. Click **Reload** on the Web tab

The `.env` (secrets) and `lostandfound.db` (data) stay on the server between deploys.

### 4.14 — What goes in your `.env`?
`SECRET_KEY`, `DATABASE_URL`, upload limits, optional SMTP credentials. Nothing in `.env` is committed (it's in `.gitignore`).

### 4.15 — What are the security weak points?
- **File uploads** — mitigated with extension allowlist + Pillow re-encoding + 3 MB cap
- **Photo visibility** — visible to any logged-in user by design; a future iteration could gate by role
- **At-rest encryption** — bundled SQLite has no per-row encryption; a hosted DB with TLS-and-at-rest encryption would be the next step
- **HTTPS** — PythonAnywhere serves over HTTPS, so traffic is encrypted in transit

---

## 5. Live URL

[https://johnjoseph1.pythonanywhere.com](https://johnjoseph1.pythonanywhere.com)

## 6. Reference Docs

- [README.md](README.md) — quick start + deployment
- [ScopeProject.md](ScopeProject.md) — full scope, milestones, risk register
- [database/schema.sql](database/schema.sql) — MySQL schema for the seven tables
- [others/prototype.html](others/prototype.html) — entity-relationship diagram
- [others/LOST-AND-FOUND.pdf](others/LOST-AND-FOUND.pdf) — original brief
