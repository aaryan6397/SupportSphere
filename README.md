# SupportSphere

> A secure, role-based Customer Support & Ticket Management System built with Flask.

SupportSphere is a professional Flask web application for managing customer-support tickets. It provides separate workspaces for Customers, Support Agents, and Administrators. The platform includes ticket lifecycle management, SLA tracking, secure authentication, internal notes, notifications, Knowledge Base articles, REST APIs, audit logging, and production-ready development tooling.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [User Roles](#user-roles)
- [Ticket Lifecycle](#ticket-lifecycle)
- [Technology Stack](#technology-stack)
- [Project Architecture](#project-architecture)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Creating an Admin](#creating-an-admin)
- [Application Workflow](#application-workflow)
- [Security Features](#security-features)
- [SLA System](#sla-system)
- [Knowledge Base](#knowledge-base)
- [Notifications](#notifications)
- [REST API](#rest-api)
- [API Token Creation](#api-token-creation)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Docker Setup](#docker-setup)
- [CI/CD](#cicd)
- [ER Diagram](#er-diagram)
- [Project Structure](#project-structure)
- [Future Scope](#future-scope)
- [Author](#author)

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Project Overview

SupportSphere helps organizations collect, assign, track, and resolve customer support requests from one centralized platform.

A customer can create a ticket, communicate with support, upload approved files, monitor ticket status, reopen unresolved issues, and provide feedback after resolution.

A support agent can view assigned tickets, send public replies, add internal team-only notes, update ticket status, and monitor SLA state.

An administrator can manage users, create agents, assign tickets, monitor workload and SLA status, view audit logs, manage Knowledge Base articles, and control account activation.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Key Features

## Authentication and Security

- Customer registration and login
- Secure password hashing using Werkzeug
- Strong password policy:
- Minimum 8 characters
- Uppercase letter
- Lowercase letter
- Number
- Secure POST-based logout
- Password visibility show/hide control
- CSRF protection for state-changing web forms
- Password reset flow with signed, expiring, one-time tokens
- Login rate limiting
- Password reset rate limiting
- Secure session configuration:
- HttpOnly cookies
- SameSite cookies
- Secure cookies configurable for production
- Production configuration validation for secret key and secure cookies
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Role-Based Access Control

SupportSphere has three backend-enforced roles:

- Customer
- Agent
- Admin

The application does not rely only on hidden frontend buttons. Authorization is enforced on the server side.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Ticket Management

- Create support tickets
- Ticket code generation
- Ticket categories
- Ticket priority levels:
- Low
- Medium
- High
- Critical
- Ticket status tracking
- Public comments and replies
- Internal notes for agents/admins
- Customer feedback after ticket resolution
- Ticket reopening
- Agent assignment and reassignment
- Secure attachment downloads
- Server-side ticket search, filtering, and pagination
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## SLA Management

- SLA deadline calculated according to priority
- SLA statuses:
- Within SLA
- At Risk
- Breached
- Completed
- First-response tracking
- Resolution timestamp tracking
- SLA deadline display in ticket details
- SLA metrics on the Admin Dashboard
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Notifications

In-app notifications are generated for:

- New ticket creation
- Ticket assignment
- Customer reply
- Agent reply
- Ticket status update
- Ticket reopening
  
Features include:

- Notification page
- Unread notification badge
- Mark single notification as read
- Mark all notifications as read
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Knowledge Base

- Admin can create Knowledge Base articles
- Edit articles
- Publish/unpublish articles
- Article categories
- Draft articles visible only to admins
- Published articles searchable by customer and agent
- Safe content display without rendering unsafe raw HTML
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Audit Logging

Important business actions are recorded in audit logs:

- User registration
- User login
- User logout
- Ticket creation
- Ticket assignment
- Ticket status changes
- Public replies
- Internal notes
- Ticket reopening
- Feedback submission
- Agent creation
- User activation/deactivation
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
### REST API

A versioned REST API is available under:

```text
/api/v1/
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
API authentication uses revocable Bearer tokens.
Important API security behavior:
- Plain API tokens are never stored in the database
- SHA-256 token hashes are stored instead
- Customer API tokens can access only customer-owned tickets
- Agent API tokens can update only assigned tickets
- Admin API tokens can assign tickets
- API errors return JSON responses
Production Readiness
- PostgreSQL-ready database configuration
- SQLite support for local development
- Dockerfile included
- Docker Compose stack included
- GitHub Actions test workflow included
- Health check endpoint:
/health
Environment-based configuration
.gitignore configured to prevent committing secrets and local files
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
User Roles
Customer
Customers can:
- Register and log in
- Create tickets
- Set category and priority
- Upload approved attachments
- View only their own tickets
- Search/filter their own tickets
- Reply publicly to tickets
- Download their authorized attachments
- Reopen resolved tickets
- Submit 1–5 star feedback
- Read published Knowledge Base articles
- Receive notifications
Agent
Agents can:
- View only assigned tickets
- Search/filter assigned tickets
- Update valid ticket statuses
- Send public replies
- Add internal notes
- View SLA status
- Receive assignment and customer-reply notifications
- Resolve assigned tickets
Admin
Administrators can:
- View all tickets
- Filter and search all tickets
- Create support agent accounts
- Assign/reassign tickets
- View SLA metrics
- View agent workload
- View workload-based assignment recommendation
- Manage user activation status
- View audit logs
- Create/edit/publish Knowledge Base articles
- View system statistics
- Access all authorized tickets
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Ticket Lifecycle
SupportSphere uses a controlled ticket lifecycle.

OPEN
  ↓
ASSIGNED
  ↓
IN PROGRESS
  ↓
WAITING FOR CUSTOMER
  ↓
RESOLVED
  ↓
CLOSED
----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Additional supported states:
REOPENED
ESCALATED
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Valid lifecycle examples:
Open → Assigned
Assigned → In Progress
In Progress → Waiting for Customer
Waiting for Customer → Resolved
Resolved → Closed
Resolved → Reopened
Closed → Reopened

Invalid transitions are rejected by backend validation.

For example:
Assigned → Closed

is not permitted directly.
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Technology Stack
Backend
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- SQLAlchemy
- Alembic
- Werkzeug
- itsdangerous

Frontend
- HTML5
- CSS3
- JavaScript
- Jinja2 templates

Database
- SQLite for local development
- PostgreSQL-ready through DATABASE_URL

Testing and Deployment
- Pytest
- Docker
- Docker Compose
- Gunicorn
- GitHub Actions
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Project Architecture
Presentation Layer
        ↓
Flask Blueprints / Routes
        ↓
Service Layer
        ↓
SQLAlchemy Models
        ↓
SQLite / PostgreSQL Database
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Service Layer
The project uses dedicated services for important business logic:
app/services/
├── audit_service.py
├── email_service.py
├── file_service.py
├── notification_service.py
├── rate_limit_service.py
├── seed_service.py
├── sla_service.py
├── ticket_query_service.py
├── ticket_service.py
└── workload_service.py
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Examples:
- ticket_service.py validates ticket lifecycle transitions.
- sla_service.py calculates SLA deadlines and SLA status.
- file_service.py validates file extensions and magic bytes.
- notification_service.py creates in-app notifications.
- audit_service.py records business events.
- rate_limit_service.py protects login and reset endpoints.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Installation
1. Clone Repository
git clone https://github.com/aaryan6397/SupportSphere.git
cd SupportSphere

2. Create Virtual Environment
Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1

3. Install Dependencies
pip install -r requirements.txt

4. Create Environment File
Copy-Item .env.example .env

5. Apply Database Migrations
flask --app run.py db upgrade

6. Run Application
python run.py

Open in browser:
http://127.0.0.1:5000
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Environment Variables
Create a .env file based on .env.example.
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=sqlite:///supportsphere.db
APP_ENV=development
FLASK_DEBUG=false
SESSION_COOKIE_SECURE=false

MAIL_SUPPRESS_SEND=true
Production Example
APP_ENV=production
SECRET_KEY=use-a-long-random-production-secret
DATABASE_URL=postgresql+psycopg://username:password@host:5432/supportsphere
SESSION_COOKIE_SECURE=true

MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-smtp-user
MAIL_PASSWORD=your-smtp-password
MAIL_DEFAULT_SENDER=no-reply@example.com
MAIL_USE_TLS=true
MAIL_SUPPRESS_SEND=false
Never commit .env to GitHub.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Running the Application
Activate the environment:
.\.venv\Scripts\Activate.ps1
Run migrations:
flask --app run.py db upgrade
Start the server:
python run.py
Application URL:
http://127.0.0.1:5000
Health endpoint:
http://127.0.0.1:5000/health
Expected response:
{
  "status": "ok"
}
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Creating an Admin
The public registration page creates Customer accounts only.
To create a real Admin account:
python create_admin.py
Then enter:
Admin email:
Admin name:
Admin password:
To convert an existing account into Admin, use the database/admin management process carefully. Do not create fake demo identities for final deployment.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Application Workflow
Customer Workflow
Customer Registration
        ↓
Customer Login
        ↓
Create Ticket
        ↓
Ticket Assigned by Admin
        ↓
Agent Reply / Customer Reply
        ↓
Status Updates
        ↓
Ticket Resolved
        ↓
Customer Feedback or Ticket Reopen
Admin Workflow
Admin Login
        ↓
View All Tickets
        ↓
Check SLA and Workload
        ↓
Assign Ticket to Agent
        ↓
Monitor Status and Audit Logs
        ↓
Manage Agents / Users / Knowledge Base
Agent Workflow
Agent Login
        ↓
View Assigned Tickets
        ↓
Check SLA Status
        ↓
Send Public Reply or Internal Note
        ↓
Update Ticket Status
        ↓
Resolve Ticket
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Security Features
Password Security
- Passwords are hashed using Werkzeug.
- Plain passwords are never stored in the database.
- Password requirements are validated on the backend.
- Password reset links are signed and time-limited.
- Password reset tokens cannot be reused after successful reset.
CSRF Protection
All state-changing browser forms are protected using CSRF tokens:
- Login
- Registration
- Ticket creation
- Ticket comments
- Feedback
- Ticket assignment
- Agent creation
- Knowledge Base actions
- User activation/deactivation
- Logout
Rate Limiting
Rate limiting is database-backed:
Login failures: 5 attempts per 15 minutes
Password reset requests: 3 attempts per 15 minutes
Too many attempts return:
429 Too Many Requests
File Upload Security
Ticket attachment validation includes:
- Allowed extension validation
- File signature / magic-byte validation
- Generated UUID storage name
- Original filename is not trusted
- Authorization check before download
- Maximum file size configuration
- Path traversal protection
Allowed attachment types:
PNG
JPG
JPEG
PDF
DOC
DOCX
Authorization Security
- Customers cannot access other customers’ tickets.
- Agents cannot access unassigned tickets.
- Customers cannot access internal notes.
- Only Admin can assign tickets.
- Only assigned Agent can change ticket status.
- Only Admin can manage user activation.
- API access is role-scoped.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SLA System
Default SLA policy:
Priority	First Response	Resolution
Critical	15 minutes	4 hours
High	1 hour	8 hours
Medium	4 hours	24 hours
Low	8 hours	48 hours

SLA statuses:
WITHIN_SLA
AT_RISK
BREACHED
COMPLETED
SLA contributes to:
- Ticket detail display
- Admin dashboard metrics
- Agent workload score
- Assignment recommendation
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Knowledge Base
The Knowledge Base supports self-service support.
Admin Features
- Create article
- Edit article
- Publish article
- Unpublish article
- Categorize article
- Keep articles as drafts

Customer/Agent Features
- Search article by keyword
- Filter article by category
- View published articles

Article categories include:
Account
Payment
Delivery
Product
Security
General
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Notifications
Notifications are created for important ticket events.
Event	Recipient
New ticket created	Admin
Ticket assigned	Agent and Customer
Agent/Admin public reply	Customer
Customer reply	Assigned Agent
Ticket status update	Customer
Ticket reopened	Assigned Agent


Users can:
- View notifications
- See unread count in navbar
- Mark one notification as read
- Mark all notifications as read
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

REST API
Base URL:
/api/v1/
Full API documentation:
docs/openapi.yaml
Authentication
API requests require a Bearer token:
Authorization: Bearer ss_your_token_here
API Endpoints
Method	Endpoint	Access
GET	/api/v1/tickets	Authorized user
POST	/api/v1/tickets	Customer
GET	/api/v1/tickets/<id>	Authorized owner/agent/admin
PATCH	/api/v1/tickets/<id>	Assigned Agent
POST	/api/v1/tickets/<id>/comments	Authorized user
POST	/api/v1/tickets/<id>/assign	Admin
POST	/api/v1/tickets/<id>/resolve	Assigned Agent


API Token Creation
Run:
flask --app run.py create-api-token
The terminal asks for:
Email
Token name
The plaintext token appears only once.
Important:
The database stores only a SHA-256 hash of the token.
Example API Request
curl -X GET http://127.0.0.1:5000/api/v1/tickets ^
  -H "Authorization: Bearer ss_your_token_here"
Example Ticket API Request
{
  "subject": "Payment deducted but order failed",
  "category": "Payment",
  "priority": "critical",
  "description": "The payment amount was deducted but my order was not completed."
}
------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Database Migrations
All schema changes use Flask-Migrate and Alembic.
Apply migrations:
flask --app run.py db upgrade
Create a migration after model changes:
flask --app run.py db migrate -m "describe change"
Apply it:
flask --app run.py db upgrade
Current schema includes:
- Users
- Tickets
- Ticket comments
- Ticket attachments
- Ticket feedback
- Audit logs
- SLA timestamps
- Internal notes
- Notifications
- Knowledge Base articles
- API tokens
- Password reset version
- Rate-limit events
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Demo Seed Data
For fictional local demonstration data only:
flask --app run.py seed-demo-data

To remove only fictional .test demo data:
flask --app run.py purge-demo-data

The purge command removes only seed-generated demo accounts and demo tickets. Real user accounts and real tickets are preserved.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Testing
Run the full test suite:
pytest -v

The project currently includes automated tests for:
- Customer registration
- Customer login
- Strong password validation
- Login rate limiting
- CSRF protection
- Password reset token reuse prevention
- Customer ticket creation
- Secure attachment validation
- Ticket lifecycle validation
- Internal note privacy
- Ticket reopening
- Role-scoped dashboard search
- Status change notifications
- Admin user activation/deactivation
- Knowledge Base publishing
- API token authentication
- API ticket ownership checks
- API ticket creation
- SLA breach detection
- SLA completion
- Workload recommendation

Expected result:
21 passed
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Docker Setup
Build and start the local Docker stack:
docker compose up --build

The Docker stack includes:
Flask application
Gunicorn
PostgreSQL database
Persistent uploads volume
Persistent database volume

Open:
http://localhost:8000

Docker configuration files:
Dockerfile
docker-compose.yml.dockerignore

For a public production deployment, configure:
- Unique production SECRET_KEY
- HTTPS
- SESSION_COOKIE_SECURE=true
- Strong PostgreSQL credentials
- Secure SMTP credentials
- Reverse proxy such as Nginx
- Database backups
- Environment secrets outside source control
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CI/CD
GitHub Actions workflow:
.github/workflows/test.yml

The workflow runs on:
Push
Pull Request
It performs:
1. Python setup
2. Dependency installation
3. Database migration
4. Test execution
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ER Diagram
Entity relationship documentation is available here:
docs/ER_DIAGRAM.md
Main relationship summary:
User
 ├── creates Tickets
 ├── is assigned Tickets
 ├── writes Ticket Comments
 ├── uploads Attachments
 ├── receives Notifications
 ├── owns API Tokens
 ├── authors Knowledge Articles
 └── generates Audit Logs

Ticket
 ├── has Comments
 ├── has Attachments
 └── has one Feedback record
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Project Structure
SupportSphere/
│
├── app/
│   ├── admin/
│   ├── agent/
│   ├── api/
│   ├── auth/
│   ├── knowledge/
│   ├── notifications/
│   ├── tickets/
│   ├── models/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   │   ├── admin/
│   │   ├── agent/
│   │   ├── auth/
│   │   ├── customer/
│   │   ├── errors/
│   │   ├── knowledge/
│   │   ├── notifications/
│   │   └── tickets/
│   ├── decorators.py
│   ├── errors.py
│   ├── extensions.py
│   ├── security.py
│   └── validators.py
│
├── config/
│   └── settings.py
│
├── docs/
│   ├── ER_DIAGRAM.md
│   └── openapi.yaml
│
├── migrations/
├── tests/
├── uploads/
├── .github/
│   └── workflows/
│       └── test.yml
│
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── create_admin.py
├── pytest.ini
├── requirements.txt
├── run.py
├── wsgi.py
└── README.md
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Future Scope
The following advanced integrations are intentionally not faked and can be added later with real credentials/configuration:
- Email verification
- Production SMTP delivery
- AWS S3 / cloud object storage
- AI ticket classification
- AI suggested agent reply
- Duplicate ticket detection
- AI Knowledge Base recommendations
- OpenAPI Swagger UI page
- JWT authentication option
- Admin-editable SLA policy screen
- Advanced analytics charts with date ranges
- Nginx reverse proxy production configuration
- Background worker for SLA/email processing
- Multi-tenant organization support
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Project Quality Checklist
- Flask application factory
-  Role-based authorization
-  Secure authentication
-  Strong password policy
-  CSRF protection
-  Password reset flow
-  Rate limiting
-  Ticket lifecycle validation
-  SLA tracking
-  Internal note privacy
-  Secure attachment validation
-  Search, filtering, pagination
-  Notifications
-  Knowledge Base
-  Audit logs
-  REST API
-  API token hashing
-  Docker support
-  PostgreSQL-ready configuration
-  GitHub Actions workflow
-  Automated tests
-  ER documentation
-  OpenAPI documentation
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Author
Aaryan Kumar
MCA Student
Project: SupportSphere — Customer Support & Ticket Management System
-------------------------------------------------------------------------
License
This project is created for academic, learning, and portfolio purposes.
