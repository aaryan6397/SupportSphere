# SupportSphere

SupportSphere is a Flask-based Customer Support & Ticket Management platform. It provides separate customer, agent, and admin workflows with secure role-based access, a structured ticket lifecycle, SLA tracking, notifications, a Knowledge Base, and an authenticated REST API.

## What is implemented

- Customer registration, login, secure POST logout, strong password rules, and CSRF protection.
- Database-backed rate limits for repeated login failures and password-reset requests.
- Expiring, one-time password-reset links delivered through environment-configured SMTP. Local development can suppress email delivery without exposing reset tokens in logs.
- Backend-enforced roles: `customer`, `agent`, and `admin`.
- Ticket lifecycle: Open → Assigned → In Progress → Waiting for Customer → Resolved → Closed, including Reopened and Escalated states. Invalid transitions are rejected by the backend.
- Public replies and agent/admin-only internal notes.
- Secure, role-checked ticket attachments with generated storage names.
- SLA status calculation: Within SLA, At Risk, Breached, and Completed.
- Server-side ticket search, filters, role-scoped visibility, and pagination.
- Admin ticket assignment plus a workload-aware agent recommendation; recommendations never auto-assign a ticket.
- In-app notifications for ticket creation, assignment, replies, status changes, and ticket reopening.
- Database-backed Knowledge Base with draft/publish workflow and search.
- Versioned REST API at `/api/v1/`, authenticated with revocable hashed Bearer tokens.

## Stack

- Python, Flask, Jinja, HTML/CSS/JavaScript
- Flask-SQLAlchemy, Flask-Migrate, Flask-Login
- SQLite for local development; PostgreSQL-ready via `DATABASE_URL`
- Pytest

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py db upgrade
python run.py
```

Open `http://127.0.0.1:5000`.

## Environment variables

```env
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=sqlite:///supportsphere.db
APP_ENV=development
FLASK_DEBUG=false
SESSION_COOKIE_SECURE=false
MAIL_SUPPRESS_SEND=true
```

For production, set `APP_ENV=production`, use a strong unique `SECRET_KEY`, use a PostgreSQL `DATABASE_URL`, and set `SESSION_COOKIE_SECURE=true` behind HTTPS. The application fails fast if production mode still uses the development secret or insecure cookies.

Set `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, and `MAIL_USE_TLS` to deliver password-reset emails through SMTP. Keep `MAIL_SUPPRESS_SEND=true` only for local development.

## User workflows

### Customer

Create and track tickets, add public replies, download permitted attachments, reopen resolved tickets, provide feedback, read published knowledge articles, and use personal API tokens.

### Agent

View only assigned tickets, update valid ticket states, add public replies or internal notes, monitor SLA status, and receive ticket notifications.

### Admin

Create agents, assign/reassign tickets, view live workload/SLA analytics, activate/deactivate customer and agent accounts, manage the Knowledge Base, inspect activity logs, and issue personal API tokens.

## REST API

The OpenAPI specification is available at [`docs/openapi.yaml`](docs/openapi.yaml).

Create a token:

```powershell
flask --app run.py create-api-token
```

Use it as a Bearer token. The plaintext token is displayed once; only its SHA-256 hash is stored.

```http
Authorization: Bearer ss_your_token_here
```

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/tickets` | List tickets visible to token owner |
| POST | `/api/v1/tickets` | Customer creates a ticket |
| GET | `/api/v1/tickets/<id>` | View authorized ticket |
| PATCH | `/api/v1/tickets/<id>` | Assigned agent changes status |
| POST | `/api/v1/tickets/<id>/comments` | Add public reply/internal note |
| POST | `/api/v1/tickets/<id>/assign` | Admin assigns ticket |
| POST | `/api/v1/tickets/<id>/resolve` | Assigned agent resolves ticket |

## Database migrations

Never edit a live database schema manually. Apply migrations with:

```powershell
flask --app run.py db upgrade
```

Current project migrations include tickets, comments, attachments, feedback, audit logs, SLA timestamps, internal notes, notifications, Knowledge Base articles, and hashed API tokens.

## Demo seed data

For fictional local demo data only:

```powershell
flask --app run.py seed-demo-data
```

It creates demo admin, agent, and customer accounts plus realistic ticket scenarios. The shared development password is `Password123`. The command refuses to run in production.

To remove only these fictional `.test` seed records later, without affecting real accounts/tickets:

```powershell
flask --app run.py purge-demo-data
```

The actual entity relationships are documented in [`docs/ER_DIAGRAM.md`](docs/ER_DIAGRAM.md).

## Testing

```powershell
pytest -v
```

The suite covers registration/login, CSRF, RBAC visibility, ticket lifecycle, internal-note privacy, reopening, dashboard search scope, notifications, Knowledge Base publishing, API token authentication, API ticket access, SLA status, and workload recommendations.

## Docker development stack

```powershell
docker compose up --build
```

Open `http://localhost:8000`. The compose file starts Flask/Gunicorn and PostgreSQL, runs migrations at container start, and keeps upload/database data in named Docker volumes. The included compose stack is for local development; use HTTPS, unique secrets, managed database backups, and secure cookies for production.

## CI

The GitHub Actions workflow at `.github/workflows/test.yml` installs dependencies, applies migrations, and runs the test suite on push and pull request.

## Current limitations / roadmap

- Email verification and password reset are not yet implemented.
- API tokens are implemented; JWT/OpenAPI documentation are not yet added.
- AI assistance is intentionally not added without a real configured provider/API key.
- Current SLA policies are centralized in code; an admin-editable SLA-policy UI is a future enhancement.
- Local attachment storage is retained for development; an S3-compatible storage adapter is a future deployment enhancement.
