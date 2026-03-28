# iscreami — Copilot Instructions

Open-source ice cream recipe calculator. FastAPI backend + React/TypeScript frontend, single Docker container, PostgreSQL database.

## Architecture

```
backend/
  api/
    app.py          # FastAPI app, load_dotenv() at top before other imports
    db.py           # SQLAlchemy engine (sync), SessionLocal, DbSession, NOT_FOUND_RESPONSE
    models.py       # SQLAlchemy ORM models
    schemas.py      # Pydantic v2 schemas (request/response)
    routes/         # FastAPI routers — ingredients, recipes, profiles, calculate
    services/       # Calculation engine — pac.py, sweetness.py, freezing.py, calculator.py
  cli/
    main.py         # Typer CLI entry point; load_dotenv() before other imports
    seed.py         # Seed categories, profiles, ~40 common ingredients
    importers/      # NZFCDB (.FT files) and USDA (CSV/JSON) importers
  alembic/          # DB migrations
  tests/            # pytest unit tests; use MagicMock for ingredients (not DB)

frontend/
  src/
    api.ts          # Typed fetch client; all calls go through request<T>()
    types.ts        # TypeScript interfaces mirroring backend Pydantic schemas
    hooks/          # useRecipeCalculator.ts — debounced calculate, state management
    components/     # Pure display components; receive props, no direct API calls
```

## Backend Conventions

- Use `from __future__ import annotations` at top of Python files if required for forward references in type hints
- SQLAlchemy ORM is **synchronous** (not async). `DbSession = Annotated[Session, Depends(get_db)]`
- Routes import `DbSession` and `NOT_FOUND_RESPONSE` from `api.db`
- Schemas are Pydantic v2 — use `model_config = ConfigDict(from_attributes=True)` on `Out` schemas
- `StrEnum` (not `str, Enum`) for enum schemas
- Composition fields are stored as `_pct` (percent per 100g) or `_mg` (milligrams per 100g)
- `sodium_mg` is mg/100g, not a percentage — multiply by `0.001` to get grams when calculating
- PAC override and POD override on an ingredient always take precedence over calculated values
- Services in `services/` are pure functions — no DB access, no FastAPI dependencies
- The `calculate()` pipeline in `calculator.py` takes `list[tuple[Ingredient, float]]` (ingredient, weight_g)

## Frontend Conventions

- TypeScript strict mode; all API response shapes defined in `types.ts`
- API calls only through functions in `api.ts` — never `fetch` directly in components
- Components are pure display — data fetching and state live in hooks or `App.tsx`
- Tailwind CSS v4 (`@tailwindcss/vite` plugin; no `tailwind.config.js`)
- **DaisyUI v5** — `@plugin "daisyui"` in `index.css`; use DaisyUI semantic tokens (`bg-base-100/200/300`, `text-base-content`, `border-base-200`, `btn`, `input`, `select`, `table`, `badge`, `join`) in preference to raw Tailwind gray classes
- Dark mode: class-based `.dark` on `<html>` for Tailwind `dark:` variants AND `data-theme="dark"/"light"` via `dataset.theme` for DaisyUI — both set by `useTheme.ts` and the anti-FOUC script in `index.html`; primary color is pink (`#ec4899` light / `#f472b6` dark)
- React Router v7 (`react-router-dom`): `BrowserRouter`, `Routes`, `Route`, `NavLink`, `Link` — routes are `/` (HomePage), `/calculator` (CalculatorView), `/ingredients` (IngredientsView), `/recipes` (RecipesView)
- Recharts for charts (freezing curve uses `LineChart`)
- TanStack React Query (`@tanstack/react-query`) for server state
- Vite proxy forwards `/api/*` to `localhost:8000` in dev

## Database / Migrations

- Run migrations: `cd backend && uv run alembic upgrade head`
- After model changes: `uv run alembic revision --autogenerate -m "description"`
- Never alter `alembic/versions/` files that have already been applied in production
- Seed data: `uv run python -m cli.main seed`

## After Every Edit

After making any code change, check the editor's Problems panel (errors and warnings) for the modified files and fix all issues before finishing. This applies to both Python files (type errors, unused imports, ruff warnings) and TypeScript/TSX files (type errors, missing props, unused variables).

## Build & Test

```bash
# Backend
cd backend
uv sync                   # Install deps
uv run pytest tests/ -v   # Tests
uv run ruff check .       # Lint

# Frontend
cd frontend
npm install
npx tsc --noEmit          # Type check
npm run build             # Production build
```

## Key Science — PAC & POD

**PAC (Potere AntiCongelante)** measures freezing point depression. Each solute has a factor relative to sucrose (=100):

- Glucose/Fructose/Allulose: 190, Erythritol: 280, Glycerin: 372, NaCl: 585, Ethanol: 743
- Sodium contributes via NaCl: `sodium_g × 2.58 × 585 / 100`
- Two conventions displayed: `pac_mix` (per 100g total mix) and `pac_water` (per 100g free water)

**POD (Potere Dolcificante)** is relative sweetness vs. sucrose (=1.0):

- Fructose: 1.7, Glucose: 0.75, Lactose: 0.16, Erythritol: 0.65

When adding new solute types, update both `PAC_FACTORS` in `services/pac.py` **and** `POD_FACTORS` in `services/sweetness.py`.

## Environment

- `.env` file in repo root; loaded by `load_dotenv()` in `app.py` and `cli/main.py`
- Required: `DATABASE_URL=postgresql://user:pass@host:5432/iscreami`
- Optional: `CORS_ORIGINS` (comma-separated), `SERVING_SIZE_G` (default 66)
- **Critical**: `load_dotenv()` must be called before any import that reads `os.environ` (e.g. `db.py` reads `DATABASE_URL` at import time)
