# Forge — Security/Correctness Findings

## 2026-07-12
- Fixed CI for Renovate TypeScript v7 upgrade (PR #97): `pnpm-lock.yaml` was stale after `package.json` changed `typescript` specifier from `~6.0.3` to `~7.0.0`. Ran `pnpm install --no-frozen-lockfile` to regenerate. Note: `typescript-eslint` v8.x does not yet support TS7 — the ESLint lint step will crash with `Cannot read properties of undefined (reading 'Cjs')` because TS7 removed `ts.Extension`. This is an upstream incompatibility; the next CI run will likely fail on the lint step.

## 2026-06-15
- Narrowed `_with_cache` ASGI wrapper from `2xx/3xx` to `2xx` only — if a redirect (3xx) were ever emitted from the `/assets/` StaticFiles mount, it would get cached for a year with `immutable`, which is incorrect. The mount only serves flat hashed files so this is currently theoretical, but the guard prevents a subtle caching bug if StaticFiles routing changes.
