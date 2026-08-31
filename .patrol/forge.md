# Forge — Security/Correctness Findings

## 2026-07-13
- Merged `origin/main` into `renovate/typescript-7.x` (PR #97). Resolved conflict in `.patrol/forge.md` — kept both previous entries.

## 2026-07-12
- Fixed CI for Renovate TypeScript v7 upgrade (PR #97): `pnpm-lock.yaml` was stale after `package.json` changed `typescript` specifier from `~6.0.3` to `~7.0.0`. Ran `pnpm install --no-frozen-lockfile` to regenerate. Note: `typescript-eslint` v8.x does not yet support TS7 — the ESLint lint step will crash with `Cannot read properties of undefined (reading 'Cjs')` because TS7 removed `ts.Extension`. This is an upstream incompatibility; the next CI run will likely fail on the lint step.

## 2026-07-13
- `pnpm/action-setup` v6's `working-directory` default (from `defaults.run.working-directory`) does NOT affect action steps — only `run:` steps. The action looks for `package.json` at the repo root by default. When the frontend lives in a subdirectory, set `package_json_file: frontend/package.json` explicitly. Same pitfall likely applies to any action that reads a project-level config file.

## 2026-07-14
- Fixed CI for PR #82 (palette/page-titles): two issues. (1) `IngredientsView.tsx` and `ProfilesView.tsx` used `useEffect` without importing it — added to React import. (2) `typescript-eslint` v8.x crashes on TS7 (`Cannot read properties of undefined (reading 'Cjs')`) — downgraded TypeScript from `~7.0.0` to `~6.0.0` (6.0.3) which is within the supported peer range.
- Narrowed `_with_cache` ASGI wrapper from `2xx/3xx` to `2xx` only — if a redirect (3xx) were ever emitted from the `/assets/` StaticFiles mount, it would get cached for a year with `immutable`, which is incorrect. The mount only serves flat hashed files so this is currently theoretical, but the guard prevents a subtle caching bug if StaticFiles routing changes.

## 2026-08-31
- CI zizmor gate (`.github/workflows/zizmor.yml`, `uvx zizmor .` — unpinned) broke after zizmor v1.30.0 released a stricter cache-poisoning audit. It flags `astral-sh/setup-uv` v10 in `ci.yml` even with the docs-recommended conditional `enable-cache: ${{ !startsWith(github.ref, 'refs/tags/') }}`, because setup-uv's control is a compound `ControlExpr::any([...])` and v1.30.0's tag-push "cache effectively disabled" heuristic only applies to a plain `ControlExpr::Field` (see `CacheControlField::extract` in `zizmor/src/audit/cache_poisoning.rs`). Any expression-valued `enable-cache` therefore stays `Conditional` → HIGH finding. The audit's own auto-fix is `enable-cache: false`; applied that (dropped the now-dead `cache-dependency-glob` too). Pre-commit zizmor pinned at v1.25.2 did NOT catch this — CI zizmor drifts because it's unpinned `uvx zizmor .`. Same failure was on main runs, not just this PR.
