# Atlas — Code Quality Findings

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
