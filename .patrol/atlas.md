# Atlas — Code Quality Findings

## 2026-08-23
- Skipped — already 2+ open PRs from me on this repo (#188 RecipeExport typing, #189 narrow try scope)

## 2026-08-18
- Duplicated `RecipeIngredient` construction loop in `recipes.py` `create_recipe` + `_sync_ingredients` — create path now delegates to the shared helper; helper gained full type annotations (`Session`, `list[RecipeIngredientInput]`), `type: ignore[arg-type]` on update path replaced with commented cast — opened PR #185

## 2026-08-17
- Duplicated `err instanceof Error ? err.message : fallback` idiom (8 sites across useRecipeCalculator.ts, RecipeCard.tsx, RecipesView.tsx, FileUploadModal.tsx) — extracted shared `errorMessage()` helper in `lib/errors.ts` — opened PR #182

## 2026-08-16
- Duplicated JSON blob-download logic in `RecipeCard.tsx` (handleExport) and `RecipesView.tsx` (handleExportAll) — extracted shared `downloadJson()` helper in `lib/download.ts`, both consumers now call it — opened PR #181

## 2026-08-15
- Triplicated sugar-field list: identical `sugar_fields` dicts in `pac.py`/`sweetness.py` plus a third hardcoded tuple in `calculator.py` sweetener breakdown — extracted shared `SUGAR_FIELDS` constant in `models.py`, all three consumers derive from it — opened PR #177
- AGENTS.md update blocked in queue session: Hermes hard-blocks writes to AGENTS.md (protected agent-instruction file) — approval always required, NOT bypassed by --yolo, fail-closed when no human channel. Queue-dispatched tasks asking to edit AGENTS.md should post the exact patch as a PR comment for interactive application; the guard forbids retrying or bypassing via terminal.

## 2026-08-14
- Duplicated eager-load options: `_RECIPE_LOAD_OPTIONS` (recipes.py, was 3× inline) and `_INGREDIENT_LOAD_OPTIONS` (ingredients.py, was 3× inline) extracted to shared module-level constants — opened PR #175

## 2026-07-28
- Dead export: unused `RecipeIngredientInput` interface in `frontend/src/types.ts` — opened PR #150

## 2026-07-25
- Dead code: 11 unused `TOOLTIPS` keys removed from `frontend/src/lib/tooltips.ts` — opened PR #139

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

## 2026-07-22
- Eliminated duplicated weighted-pct calculation loop in `calculator.py:calculate_nutrition` — inline loop replaced with shared `_weighted_pct` helper. Fixed misleading `</div>` indent in `RecipeHeader.tsx`. Opened PR #125.

## 2026-07-23
- Skipped — no code quality issues worth fixing today (tsc clean, ruff passes, 136 tests pass, no dead exports or imports)

## 2026-07-24
- Narrowed bare `# type: ignore` to `# type: ignore[misc]` in `schemas.py:231`; inlined redundant `export_data` return in `recipes.py:105-106` — opened PR #133

## 2026-07-26
- Skipped — no code quality issues worth fixing today (ruff clean, tsc clean, 136 tests pass, no dead code or exports)

## 2026-07-27
- Skipped — no code quality issues worth fixing today (ruff clean, pytest 136 pass, tsc clean, all TOOLTIPS keys consumed, no dead code/exports)

## 2026-07-29
- Skipped — no code quality issues worth fixing today (ruff clean, pytest 136 pass, tsc clean, no dead code/exports, no duplicated logic, no any types)

## 2026-07-30
- Skipped — no code quality issues worth fixing today (ruff clean, pytest 136 pass, tsc clean, no dead code/exports, no duplicated logic, no overly complex functions)

## 2026-07-31
- Skipped — no code quality issues worth fixing today (ruff clean, pytest 136 pass, tsc clean, no dead code/exports, no any types, no duplicated logic, no overly complex functions)

## 2026-08-01
- Dead code: orphan `RecipePickerModal` component (frontend/src/components/RecipePickerModal.tsx) never imported since Initial commit — load-recipe flow already served by RecipeCard → /calculator/:recipeId. Removed. Also removed unused `RecipeIngredientOut` type export from types.ts (schema still used by RecipeSchema).

## 2026-08-13
- Dead exports: 6 zod response schemas in `frontend/src/types.ts` (IngredientSchema, RecipeSchema, etc.) exported but never used as runtime values — only z.infer type derivation. Converted to plain interfaces (restores AGENTS.md convention); input schemas stay zod. Opened PR #174.

## 2026-08-25
- Skipped — already 2+ open PRs from me on this repo (#188 RecipeExport typing, #189 narrow try scope)

## 2026-08-27
- Skipped — already 2+ open PRs from me on this repo (#188 RecipeExport typing, #189 narrow try scope)

## 2026-08-28
- Skipped — already 2+ open PRs from me on this repo (#188 RecipeExport typing, #189 narrow try scope)

## 2026-08-29
- Skipped — already 2+ open PRs from me on this repo (#188 RecipeExport typing, #189 narrow try scope)

## 2026-08-31
- Skipped — already 2+ open PRs from me on this repo (#188 RecipeExport typing, #189 narrow try scope)
