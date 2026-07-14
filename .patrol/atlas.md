# Atlas — Code Quality Findings

## 2026-07-14
- Renamed `_MAX_RECIPE_INGREDIENTS` (private naming) → `MAX_RECIPE_INGREDIENTS` (public) — used across `schemas.py`, `export.py`, and `routes/recipes.py`. Removed the unnecessary `_MAX_IMPORT_INGREDIENTS` alias from `routes/recipes.py` (was dead code even as an alias). `export.py` now imports `MAX_RECIPE_INGREDIENTS` from `schemas` instead of hardcoding 100.
- Unused `fetchIngredient` export in `api.ts` removed — genuinely dead, no consumers

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

## 2026-07-07
- Dead code: unused `ingredient` and `profile` pytest fixtures in `backend/tests/conftest.py` — opened PR #85
