# Atlas — Code Quality Findings

## 2026-06-14
- Dead code: `ImportErrorResponse` model in `backend/api/schemas.py` — defined but never imported or referenced anywhere. Opened PR #20.

## 2026-06-15
- Dead code: `build_export_batch` function in `backend/api/services/export.py` — defined but never imported or called anywhere. Opened PR #24.
