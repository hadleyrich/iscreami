# Forge — Security/Correctness Findings

## 2026-09-01
- zizmor v1.30.0 `cache-poisoning` audit now flags the `enable-cache: ${{ !startsWith(github.ref, 'refs/tags/') }}` pattern on `astral-sh/setup-uv` pinned at v10.x. The audit's conditional-disable heuristic only applies to plain boolean control fields; setup-uv's coordinate is an `any([...])` composite (Exact("true") for v10+, boolish for <v10), so `CacheControlField::extract` never matches and any expression is treated as Conditional → high-severity finding + unsafe auto-fix → CI fails (exit 14). Fix verified against v1.30.0: set `enable-cache: false` (zizmor's own auto-fix). Applied in PR #193 (same change as PR #186). Removing the field entirely is also safe for zizmor but explicit `false` is clearer.

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

## 2026-09-06
- Renewed pnpm lockfile-staleness failure (first seen 2026-07-12, PR #97; also PR #202 for 12.3.0): Renovate bumped `packageManager` to `pnpm@12.3.1` in `frontend/package.json` but its artifact update crashed before touching the lockfile (`Install tool node@24.20.0 failed` — VersionService @postConstruct error; same crash also listed `frontend/package-lock.json`, which is a stale npm artifact never updated by pnpm PRs). CI failed with `ERR_PNPM_FROZEN_LOCKFILE_WITH_OUTDATED_LOCKFILE` on `pnpm install --frozen-lockfile` because `packageManagerDependencies` in `pnpm-lock.yaml` still pinned 12.3.0. Fix (PR #204 branch): ran `pnpm install --lockfile-only` with pnpm 12.3.1 from a temp prefix — lockfile diff is purely the pnpm/packageManagerDependencies self-pins, no dependency churn. Reminder: pnpm ≥9.9 records the package manager itself in the lockfile, so ANY bump of the `packageManager` field requires regenerating the lockfile with the target pnpm version.
