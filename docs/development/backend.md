# Backend Developer Guide

This guide covers everything you need to know to work on the iscreami Python/FastAPI backend: architecture, coding conventions, database patterns, testing, and the calculation engine.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Environment](#development-environment)
3. [Project Structure](#project-structure)
4. [Coding Conventions](#coding-conventions)
5. [API Layer](#api-layer)
6. [Database & Migrations](#database--migrations)
7. [Calculation Engine](#calculation-engine)
8. [CLI Tools](#cli-tools)
9. [Testing](#testing)
10. [Linting & Formatting](#linting--formatting)

---

## Architecture Overview

The backend is a synchronous FastAPI application backed by a PostgreSQL database. The key design principle is a strict separation of concerns:

```
HTTP Request → routes/ (FastAPI router)
                  ↓
             db.py (SQLAlchemy session)
                  ↓
             models.py (ORM queries)
                  ↓
             services/ (pure calculation functions)
                  ↓
             schemas.py (Pydantic response serialisation)
```

- **Routes** handle HTTP I/O and dependency injection only — no business logic.
- **Services** are pure functions. They receive plain Python objects (ORM model instances or simple data structures) and return result dataclasses. They have **no database access** and **no FastAPI dependencies**.
- **Models** are SQLAlchemy ORM models with no business logic.
- **Schemas** are Pydantic v2 models used for request validation and response serialisation only.

---

## Development Environment

### Prerequisites

- Python 3.13+
- PostgreSQL 14+
- [`uv`](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# From the repo root
cp .env.example .env
# Edit .env — at minimum set DATABASE_URL

cd backend
uv sync          # Install all dependencies (including dev deps)
```

### Running the Development Server

```bash
cd backend
uv run uvicorn api.app:app --reload
# API available at http://localhost:8000
# OpenAPI docs at http://localhost:8000/api/v1/docs
```

### Environment Variables

The `.env` file lives in the **repo root** and is loaded automatically by Pydantic Settings in `api/settings.py`. The `settings` object is imported by `app.py` and `cli/main.py`, which auto-loads the `.env` file.

| Variable         | Required | Default                                | Description                                     |
| ---------------- | -------- | -------------------------------------- | ----------------------------------------------- |
| `DATABASE_URL`   | Yes      | `postgresql://localhost:5432/iscreami` | PostgreSQL connection string                    |
| `CORS_ORIGINS`   | No       | `*`                                    | Comma-separated list of allowed CORS origins    |
| `SERVING_SIZE_G` | No       | `66`                                   | Default serving size for nutrition calculations |

> Environment variables are **type-validated at startup** by Pydantic Settings. If any required variable is missing or invalid, the application will fail immediately with a clear error message.

---

## Project Structure

```
backend/
├── api/
│   ├── app.py          # FastAPI application, CORS, static file serving
│   ├── db.py           # SQLAlchemy engine, SessionLocal, DbSession, NOT_FOUND_RESPONSE
│   ├── models.py       # SQLAlchemy ORM models
│   ├── schemas.py      # Pydantic v2 request/response schemas
│   ├── routes/
│   │   ├── calculate.py    # POST /calculate
│   │   ├── ingredients.py  # CRUD for ingredients and categories
│   │   ├── recipes.py      # CRUD for recipes + export/import
│   │   └── profiles.py     # CRUD for target profiles
│   └── services/
│       ├── calculator.py   # Orchestrates all sub-calculators
│       ├── composition.py  # Per-ingredient composition calculations
│       ├── export.py       # Recipe export/import helpers
│       ├── pac.py          # PAC (freezing point depression) calculation
│       ├── sweetness.py    # POD (relative sweetness) calculation
│       └── freezing.py     # Freezing point & curve calculation
├── cli/
│   ├── main.py         # Typer CLI entry point
│   ├── seed.py         # Seed categories, profiles, ~40 common ingredients
│   └── importers/
│       ├── base.py         # Abstract base importer
│       ├── nzfcdb.py       # NZFCDB (.FT file) importer
│       └── usda.py         # USDA FDC (CSV/JSON) importer
├── alembic/
│   ├── env.py          # Migration environment (reads DATABASE_URL)
│   └── versions/       # Migration scripts (do not edit applied migrations)
└── tests/
    └── test_calculator.py  # Unit tests for the calculation engine
```

---

## Coding Conventions

### Python Version & Type Hints

- Target Python **3.13+**.
- Use `from __future__ import annotations` at the top of files that need forward references in type hints (e.g. when a class references itself).
- Annotate all function signatures with types. Return types are mandatory.

### Imports

Follow this order (enforced by ruff):

1. Standard library
2. Third-party packages
3. Local application imports

Since configuration is now handled by Pydantic Settings (not `load_dotenv()`), imports can follow standard PEP 8 ordering without workarounds.

### Enums

Use `StrEnum` (not `str, Enum`) for string-valued enums in schemas:

```python
from enum import StrEnum

class RecipeType(StrEnum):
    ice_cream = "ice_cream"
    gelato = "gelato"
```

### Composition Fields

Ingredient composition values follow a consistent naming convention:

- `_pct` suffix → percentage per 100 g (e.g. `water_pct`, `total_fat_pct`)
- `_mg` suffix → milligrams per 100 g (used only for `sodium_mg`)

When using `sodium_mg` in calculations, convert to grams first: `sodium_mg * 0.001`.

### PAC & POD Overrides

An ingredient's `pac_override` and `pod_override` fields always take precedence over calculated values. Check for overrides **before** running any calculation:

```python
if ingredient.pac_override is not None:
    return float(ingredient.pac_override)
# ... calculate normally
```

### FastAPI Route Conventions

```python
from api.db import DbSession, NOT_FOUND_RESPONSE
from api.schemas import IngredientOut

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.get("/{id}", response_model=IngredientOut, responses=NOT_FOUND_RESPONSE)
def get_ingredient(id: str, db: DbSession) -> IngredientOut:
    ingredient = db.get(Ingredient, id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient
```

Key points:

- Import `DbSession` (type alias) and `NOT_FOUND_RESPONSE` from `api.db`.
- Use `responses=NOT_FOUND_RESPONSE` for any endpoint that can return 404.
- Always return the Pydantic schema type; FastAPI handles serialisation via `response_model`.
- Use `status_code=201` for `POST` endpoints that create resources.
- Use `status_code=204` (no content) for `DELETE` endpoints.

### Pydantic Schemas

- All `Out` schemas (response models) use `model_config = ConfigDict(from_attributes=True)` to enable ORM serialisation:

```python
from pydantic import BaseModel, ConfigDict

class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    # ...
```

- `Create` schemas contain all required fields for creating a resource.
- `Update` schemas make all fields optional (for partial updates via `PUT`).
- Computed or derived fields (e.g. `pac`, `pod`) are included in `Out` schemas only.

---

## API Layer

### Base URL

All API endpoints are mounted under `/api/v1`. The health check at `/api/v1/health` returns `{"status": "ok"}`.

### Endpoint Summary

| Method   | Path                            | Description                         |
| -------- | ------------------------------- | ----------------------------------- |
| `GET`    | `/api/v1/health`                | Health check                        |
| `GET`    | `/api/v1/ingredients`           | List/search ingredients (paginated) |
| `GET`    | `/api/v1/ingredients/{id}`      | Get ingredient by ID                |
| `POST`   | `/api/v1/ingredients`           | Create ingredient                   |
| `PUT`    | `/api/v1/ingredients/{id}`      | Update ingredient                   |
| `DELETE` | `/api/v1/ingredients/{id}`      | Delete ingredient                   |
| `GET`    | `/api/v1/ingredient-categories` | List ingredient categories          |
| `GET`    | `/api/v1/recipes`               | List recipes (paginated)            |
| `GET`    | `/api/v1/recipes/{id}`          | Get recipe by ID                    |
| `POST`   | `/api/v1/recipes`               | Create recipe                       |
| `PUT`    | `/api/v1/recipes/{id}`          | Update recipe                       |
| `DELETE` | `/api/v1/recipes/{id}`          | Delete recipe                       |
| `GET`    | `/api/v1/recipes/{id}/export`   | Export a single recipe as JSON      |
| `GET`    | `/api/v1/recipes/export-all`    | Export all recipes as JSON array    |
| `POST`   | `/api/v1/recipes/import`        | Import recipes from JSON file       |
| `GET`    | `/api/v1/target-profiles`       | List target profiles                |
| `GET`    | `/api/v1/target-profiles/{id}`  | Get target profile by ID            |
| `POST`   | `/api/v1/target-profiles`       | Create target profile               |
| `PUT`    | `/api/v1/target-profiles/{id}`  | Update target profile               |
| `DELETE` | `/api/v1/target-profiles/{id}`  | Delete target profile               |
| `POST`   | `/api/v1/calculate`             | Calculate metrics for a recipe      |

Full interactive documentation is available at `/api/v1/docs` when the server is running.

### Adding a New Route

1. Create a new file in `backend/api/routes/`.
2. Define an `APIRouter` with a `prefix` and `tags`.
3. Import and register the router in `backend/api/app.py`:

```python
from api.routes import my_new_route
api.include_router(my_new_route.router)
```

---

## Database & Migrations

### SQLAlchemy

The ORM is **synchronous** SQLAlchemy 2.x (not async). Do not use `AsyncSession` or `async def` in database operations.

```python
# Correct — synchronous session usage
def get_ingredient(id: str, db: DbSession) -> Ingredient | None:
    return db.get(Ingredient, id)

# Correct — query with filter
def search_ingredients(q: str, db: DbSession) -> list[Ingredient]:
    return db.scalars(
        select(Ingredient).where(Ingredient.name.ilike(f"%{q}%"))
    ).all()
```

### Model Conventions

- Primary keys on most models are `String` UUIDs (generated in Python, not the database). Exception: `IngredientCategory`, `IngredientAlias`, `TargetProfile` use auto-increment integers.
- Relationships use `back_populates` for bidirectionality.
- Timestamps (`created_at`, `updated_at`) use `server_default=func.now()` and `onupdate=func.now()`.

### Migrations with Alembic

After changing `models.py`, always generate a new migration:

```bash
cd backend
uv run alembic revision --autogenerate -m "short description of change"
uv run alembic upgrade head
```

**Rules:**

- Never edit migration files that have already been applied to production (any file in `alembic/versions/` that predates your branch).
- Always review the auto-generated migration before committing — Alembic can miss things like index changes or constraint renames.
- The Alembic `env.py` reads `DATABASE_URL` from the environment. Ensure your `.env` file is properly configured before running migrations (Pydantic Settings will auto-load it when you run `uv run alembic upgrade head`).

---

## Calculation Engine

The calculation engine lives in `backend/services/` and is entirely composed of **pure functions** — no database access, no FastAPI dependencies.

### Entry Point

`calculator.py:calculate()` is the main orchestrator:

```python
def calculate(
    items: list[tuple[Ingredient, float]],  # (ingredient, weight_g)
    target_profile: TargetProfile | None = None,
    serving_size_g: float = 66.0,
) -> CalculateResponse:
```

It calls each sub-calculator in sequence and assembles the final response.

### Sub-Calculators

#### `pac.py` — Freezing Point Depression Power

PAC (Potere AntiCongelante) measures a solute's ability to depress the freezing point, relative to sucrose (PAC = 100).

**Adding a new solute:** Add its PAC factor to `PAC_FACTORS` in `pac.py`.

```python
PAC_FACTORS: dict[str, float] = {
    "sucrose": 100.0,
    "glucose": 190.0,
    "fructose": 190.0,
    "lactose": 100.0,
    "maltose": 100.0,
    "galactose": 190.0,
}
NACL_PAC_FACTOR = 585.0
ETHANOL_PAC_FACTOR = 743.0
SODIUM_TO_NACL = 2.58  # NaCl/Na mass ratio
```

The calculation uses **advanced mode** (individual sugar fractions) when breakdown fields are present, and falls back to **simple mode** (treat total sugar as sucrose) otherwise.

#### `sweetness.py` — Relative Sweetness

POD (Potere Dolcificante) is relative sweetness per unit mass compared to sucrose (POD = 1.0).

**Adding a new sweetener:** Add its factor to `POD_FACTORS` in `sweetness.py`.

> When adding a new solute type, update **both** `PAC_FACTORS` in `pac.py` **and** `POD_FACTORS` in `sweetness.py` if it is also a sweetener.

#### `freezing.py` — Freezing Point & Curve

Uses the Pickering (1891) empirical table (60 anchor points) with linear interpolation to convert PAC to freezing point depression. An additional salt correction from Leighton (1927) is applied for MSNF content.

The freezing curve models the self-reinforcing concentration effect as ice forms, using a binary-search approach at each temperature step.

See [`docs/freezing-calculations.md`](../freezing-calculations.md) for the full mathematical derivation.

### Extending the Calculator

To add a new metric to the `calculate()` response:

1. Add a new pure function (or extend an existing one) in `services/`.
2. Add the corresponding result schema to `schemas.py`.
3. Update `CalculateResponse` in `schemas.py` to include the new field.
4. Call the new function in `calculator.py:calculate()` and populate the response field.
5. Add unit tests in `tests/test_calculator.py`.

---

## CLI Tools

The CLI uses [Typer](https://typer.tiangolo.com/) and is invoked via:

```bash
cd backend
uv run python -m cli.main <command>
```

### Available Commands

```bash
# Seed categories, target profiles, and ~40 common ingredients
uv run python -m cli.main seed

# Import from NZFCDB (.FT files)
uv run python -m cli.main import nzfcdb --data-dir /path/to/data --food-id F10019
uv run python -m cli.main import nzfcdb --data-dir /path/to/data --all

# Import from USDA FDC
uv run python -m cli.main import usda --data-dir /path/to/data --fdc-id 746782
```

### Adding a New CLI Command

1. Add a new subcommand to `cli/main.py` using the `@app.command()` decorator.
2. Environment variables are automatically loaded by Pydantic Settings when running any CLI command (no manual setup needed).

---

## Testing

See the [Testing Guide](./testing.md) for comprehensive documentation on:

- Running tests by type (unit, integration, all)
- Coverage reporting and HTML reports
- Database fixtures for integration tests
- Mock fixtures for unit tests
- Best practices and CI/CD workflows

**Quick reference:**

```bash
# All tests with coverage
uv run pytest tests/ -v

# Unit tests only (fast)
uv run pytest tests/ -m "not integration"

# Integration tests only
uv run pytest tests/ -m integration
```

The backend currently has:

- **Unit tests**: Comprehensive coverage of calculation engine, composition, schemas (~130 tests, 98%+ coverage)
- **Integration tests**: Round-trip testing (export/import workflows)
- **API route tests**: Not yet implemented — a good area to add integration tests

The test suite uses `pytest` with:

- Mock factories (`ingredient`, `profile` fixtures) for unit tests
- ORM factories (`test_db`, `db_ingredient_factory`, etc.) for integration tests
- Automated coverage reporting with `pytest-cov`
- Test markers (`@pytest.mark.unit`, `@pytest.mark.integration`) for organizing tests

---

## Linting & Formatting

The project uses [ruff](https://docs.astral.sh/ruff/) for both linting and formatting.

```bash
cd backend
uv run ruff check .          # Lint (reports issues)
uv run ruff check . --fix    # Lint and auto-fix safe issues
uv run ruff format .         # Format (opinionated, black-compatible)
```

The `ruff` configuration is in `pyproject.toml`. Key rules enforced:

- PEP 8 style (line length, spacing)
- Unused imports flagged (`F401`)
- Import order (`I001`) — standard lib → third-party → local
- `E402` for imports that must appear after `load_dotenv()` (suppressed with `# noqa: E402`)

Always run `ruff check .` before committing.
