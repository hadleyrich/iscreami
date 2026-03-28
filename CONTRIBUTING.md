# Contributing to iscreami

Thank you for your interest in contributing! This document is the starting point for new contributors. It covers the development workflow, branch strategy, and links to the detailed per-area guides.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Development Guides](#development-guides)
3. [Setting Up Your Environment](#setting-up-your-environment)
4. [Development Workflow](#development-workflow)
5. [Branch & Commit Strategy](#branch--commit-strategy)
6. [Running the Full Stack Locally](#running-the-full-stack-locally)
7. [Tests, Linting & Type Checking](#tests-linting--type-checking)
8. [Making a Change — Checklist](#making-a-change--checklist)

---

## Project Overview

**iscreami** is an open-source ice cream recipe calculator. The user enters ingredients with weights and the app calculates real-time freezing properties (PAC), relative sweetness (POD), composition, and nutrition.

**Stack:**

| Layer      | Technology                                                       |
| ---------- | ---------------------------------------------------------------- |
| Backend    | Python 3.13, FastAPI, SQLAlchemy (sync), PostgreSQL              |
| Frontend   | React 19, TypeScript (strict), Vite, Tailwind CSS v4, DaisyUI v5 |
| Deployment | Single Docker container, `uv` for Python deps, npm for JS deps   |

---

## Development Guides

For in-depth coverage of coding conventions, architecture, and patterns:

- **[Backend Developer Guide](docs/development/backend.md)** — FastAPI, SQLAlchemy, Alembic migrations, calculation engine, CLI tools, testing.
- **[Frontend Developer Guide](docs/development/frontend.md)** — React, TypeScript, api.ts, hooks, DaisyUI/Tailwind UI conventions, theming.
- **[Freezing Calculations](docs/freezing-calculations.md)** — Mathematical derivation of PAC, freezing point, and freezing curve algorithms.

---

## Setting Up Your Environment

### Prerequisites

| Tool       | Version | Notes                                                              |
| ---------- | ------- | ------------------------------------------------------------------ |
| Python     | 3.13+   |                                                                    |
| Node.js    | 20+     |                                                                    |
| PostgreSQL | 14+     | Must be running locally                                            |
| `uv`       | latest  | [Install](https://docs.astral.sh/uv/getting-started/installation/) |

### First-time Setup

```bash
# 1. Clone the repo
git clone https://github.com/hadleyrich/iscreami.git
cd iscreami

# 2. Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL to your local PostgreSQL connection string

# 3. Create the database
psql -U postgres -c "CREATE DATABASE iscreami OWNER postgres;"

# 4. Install backend dependencies
cd backend
uv sync

# 5. Run database migrations
uv run alembic upgrade head

# 6. Seed initial data (categories, profiles, ~40 common ingredients)
uv run python -m cli.main seed

# 7. Install frontend dependencies
cd ../frontend
pnpm install
```

---

## Development Workflow

### Running the Stack

Open two terminals:

**Terminal 1 — Backend:**

```bash
cd backend
uv run uvicorn api.app:app --reload
# API: http://localhost:8000
# OpenAPI docs: http://localhost:8000/api/v1/docs
```

**Terminal 2 — Frontend:**

```bash
cd frontend
pnpm dev
# App: http://localhost:5173
# Vite proxies /api/* → localhost:8000
```

### After Changing Backend Models

Always create and apply a migration:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
```

---

## Branch & Commit Strategy

- Branch from `main` for every change.
- Branch names: `feature/short-description`, `fix/short-description`, `docs/short-description`.
- Commit messages should be short, present-tense, imperative: `Add PAC override field`, `Fix freezing curve at zero PAC`.
- Open a pull request against `main` when your change is ready for review.

---

## Running the Full Stack Locally

To test the production Docker build locally:

```bash
docker build -t iscreami .
docker run \
  -e DATABASE_URL=postgresql://user:pass@host.docker.internal:5432/iscreami \
  -p 8000:8000 \
  iscreami
```

The container serves both the API (`/api/v1/*`) and the compiled frontend on port 8000.

---

## Tests, Linting & Type Checking

Run all checks before opening a PR:

```bash
# Backend — all tests with coverage
cd backend
uv run pytest tests/ -v

# Backend — unit tests only (fast)
uv run pytest tests/ -m "not integration"

# Backend — lint
uv run ruff check .

# Frontend — type check
cd frontend
pnpm tsc --noEmit
```

See [Testing Guide](docs/development/testing.md) for comprehensive testing documentation, including:

- Running tests by type (unit, integration)
- Coverage reporting
- Using fixtures for test data
- Best practices

### What is Tested

The test suite in `backend/tests/` includes:

- **Unit tests**: Calculation engine (PAC, POD, freezing, composition, nutrition, target profile comparison) — uses `MagicMock` fixtures for ingredient and profile objects
- **Integration tests**: Export/import workflows with real SQLite database
- **Coverage**: 98%+ on services and schemas; routes not yet covered (good area for new integration tests)

New calculation logic should always be accompanied by unit tests. New API endpoints should have corresponding integration tests.

---

## Making a Change — Checklist

Use this checklist when preparing a PR:

**Backend changes:**

- [ ] All tests pass: `uv run pytest tests/`
- [ ] ORM model changes have a corresponding Alembic migration
- [ ] New routes import `DbSession` and `NOT_FOUND_RESPONSE` from `api.db`
- [ ] New calculation logic is in `services/` as a pure function (no DB access)
- [ ] `pac_override` / `pod_override` fields are checked before any calculation
- [ ] New Pydantic `Out` schemas have `model_config = ConfigDict(from_attributes=True)`
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check .` reports no issues

**Frontend changes:**

- [ ] New API calls are added to `api.ts` using `request<T>()`
- [ ] New types / response shapes are added to `types.ts`
- [ ] Components are pure display (no direct `fetch` calls)
- [ ] DaisyUI semantic colour tokens used (not raw Tailwind grey classes)
- [ ] Dark mode works correctly (test by toggling the theme toggle)
- [ ] `npx tsc --noEmit` reports no errors
