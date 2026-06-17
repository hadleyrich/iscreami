# Bolt — Performance Findings

## 2026-06-11
- Fixed N+1 query for `target_profile` in recipe endpoints (`list_recipes`, `_load_recipe`, `export_all_recipes`) — added `joinedload(Recipe.target_profile)` to all recipe queries to avoid lazy-loading the target profile once per recipe row during serialization. Opened PR #11.

## 2026-06-13
- Replaced joinedload with selectinload for Recipe.ingredients in list_recipes and export_all_recipes to avoid cartesian product on shared ingredients — opened PR #14

## 2026-06-14
- Fixed same joinedload→selectinload pattern in _load_recipe helper (affects get_recipe, export_single_recipe, create_recipe, update_recipe, import_recipes) — opened PR #19

## 2026-06-15
- Added Cache-Control headers to Vite-built static assets — immutable (1yr) for /assets/*, no-cache for index.html — opened PR #23

## 2026-06-16
- Configured React Query QueryClient defaults: staleTime=30s, refetchOnWindowFocus=false, retry=1 — prevents unnecessary API refetches on every page navigation; mutations already invalidate caches so data freshness is preserved — opened PR #29

## 2026-06-17
- Reduced freezing-curve compute overhead by ~50%: halved binary-search iterations (60→30) in `frozen_water_fraction()` and lowered `min_temp` from -40°C to -30°C to match chart Y-axis domain — opened PR #32

## 2026-06-18
- Skipped — no clear performance bottleneck after inspecting all backend routes (no new N+1), frontend components (no excessive re-renders, proper debounce), calculator service (already optimized in PR #32), and DB schema (acceptable at current scale)
