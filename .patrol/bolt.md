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
- Configured React Query QueryClient defaults: staleTime=30s, refetchOnWindowFocus=false, retry=1 — prevents unnecessary API refetches on every page navigation; mutations already invalidate caches so data freshness is preserved
