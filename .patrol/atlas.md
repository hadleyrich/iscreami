# Atlas — Code Quality Findings

## 2026-07-14
- Renamed `_MAX_RECIPE_INGREDIENTS` (private naming) → `MAX_RECIPE_INGREDIENTS` (public) — used across `schemas.py`, `export.py`, and `routes/recipes.py`. Removed the unnecessary `_MAX_IMPORT_INGREDIENTS` alias from `routes/recipes.py` (was dead code even as an alias). `export.py` now imports `MAX_RECIPE_INGREDIENTS` from `schemas` instead of hardcoding 100.
- Unused `fetchIngredient` export in `api.ts` removed — genuinely dead, no consumers

## 2026-07-11
- Moved `_MAX_IMPORT_INGREDIENTS` from `recipes.py` to `export.py` where the validation logic lives — replaced hardcoded `100` with named constant, updated error message to interpolate it

## 2026-07-09
- Dead code: unused `_MAX_IMPORT_INGREDIENTS` constant in `backend/api/routes/recipes.py` — defined but never referenced. Removed.

## 2026-07-08
- Remaining manual Escape key listeners in IngredientsView and ProfilesView replaced with shared `useEscape` hook — opened PR #90

## 2026-07-04
- Duplicated data: `SOURCE_LABELS` and `ALL_SOURCES` both defined same key→label mapping — derived `ALL_SOURCES` from `SOURCE_LABELS` via `Object.entries()`, opened PR #72

## 2026-07-05
- Duplicated Escape key handler extracted into shared `useEscape` hook — 9 instances across 7 files replaced with one-line hook call, opened PR #76

## 2026-07-03
- importRecipes duplicated fetch/error-handling logic because `request()` helper set Content-Type on FormData bodies — fixed both, opened PR #63

## 2026-06-18
- Remaining inline imports in `test_calculator.py` — opened PR #37

## 2026-06-16
- Consolidate ~146 inline imports to module level across 6 test files — opened PR #30

## 2026-06-17
- Redundant side-effect import in `cli/main.py` (`from api.settings import settings  # noqa: F401`) — opened PR #33

## 2026-06-15
- Dead code: `build_export_batch` function in `backend/api/services/export.py` — defined but never imported or called anywhere. Opened PR #24.

## 2026-06-14
- Dead code: `ImportErrorResponse` model in `backend/api/schemas.py` — defined but never imported or referenced anywhere. Opened PR #20.

## 2026-07-19
- Moved type-only imports (Callable, starlette types, Session, Iterator, Path) behind TYPE_CHECKING blocks in app.py, base.py, usda.py — opened PR #116
## 2026-07-17
- Wired up `serving_size_g` setting: was defined in Settings but never consumed — now imported by schemas.py and calculator.py to replace hardcoded 66.0 defaults. Opened PR #110.

## 2026-07-15
- Dead code: `_MAX_IMPORT_INGREDIENTS` constant in `backend/api/services/export.py` — defined but never referenced (validation uses `MAX_RECIPE_INGREDIENTS` from schemas). Opened PR #105.

## 2026-07-07
- Dead code: unused `ingredient` and `profile` pytest fixtures in `backend/tests/conftest.py` — opened PR #85

## 2026-07-21
- Unreliable `f == 0.0` float equality in `test_freezing.py:151,156` — replaced with `pytest.approx(0.0)`. Opened PR #122
## 2026-07-18
- Dead export: `TooltipKey` in `frontend/src/lib/tooltips.ts` — defined but never imported. Opened PR #114.
