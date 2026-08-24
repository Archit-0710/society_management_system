# Society Maintenance Tracker

Society Maintenance Tracker is a full-stack application for managing residential-society maintenance. Residents can submit and track complaints, while administrators can manage categories, priorities, statuses, notices, notifications, and dashboard statistics.

## Features

- Resident registration, login, and profile access using JWT authentication
- Complaint creation, history, priority, status, and admin management
- Category and notice management for administrators
- Dashboard statistics and administrator notifications
- Local upload serving through the API, with optional ImageKit integration
- PostgreSQL persistence with Alembic migrations

## Stack

- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic Settings
- **Frontend:** React 19, React Router, Vite
- **Tooling:** uv, npm, Docker Compose

## Project Structure

```text
backend/       FastAPI application, models, migrations, and tests
frontend/      React/Vite client
docker-compose.yml
pyproject.toml
uv.lock
```

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm
- Docker Desktop with Docker Compose

## Local Setup

### 1. Start PostgreSQL

From the repository root:

```powershell
docker compose up -d
```

The default development database is available at `localhost:5432` with database `society_db`, user `postgres`, and password `postgres`.

### 2. Configure the backend

Create `backend/.env` from the example and update secrets as needed:

```powershell
Copy-Item backend/.env.example backend/.env
```

At minimum, set a strong `JWT_SECRET_KEY`. The example contains the local PostgreSQL connection string. ImageKit and email settings are optional unless those integrations are used.

### 3. Install dependencies and migrate

```powershell
uv sync
Set-Location backend
uv run alembic upgrade head
```

### 4. Create an administrator

Run this from the `backend` directory. The command prompts for the password without exposing it in shell history:

```powershell
uv run python create_admin.py --email admin@example.com --name "Society Admin"
```

### 5. Run the backend

```powershell
uv run uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

Useful health checks:

```text
GET /health
GET /health/db
```

### 6. Run the frontend

In a second terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. During development, Vite proxies `/api` and `/uploads` to `http://localhost:8000`. For a deployed frontend, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL` to the deployed API URL.

## Development Commands

Backend commands should be run from `backend/`:

```powershell
$env:PYTHONPATH = (Get-Location).Path
uv run --with pytest --with httpx2 python -m pytest
uv run alembic upgrade head
```

Frontend commands should be run from `frontend/`:

```powershell
npm run lint
npm run build
npm run preview
```

## API Areas

The backend exposes routes under `/api` for authentication, categories, complaints, notices, notifications, and dashboard data. Administrator-only operations use the `/api/admin/...` path. Uploaded local files are served under `/uploads`.

## Stopping Services

Stop the local PostgreSQL container with:

```powershell
docker compose down
```

Add `-v` only when you intentionally want to remove the persisted `pgdata` database volume.
