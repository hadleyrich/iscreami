# Forge — Security/Correctness Findings

## 2026-07-13
- `pnpm/action-setup` v6's `working-directory` default (from `defaults.run.working-directory`) does NOT affect action steps — only `run:` steps. The action looks for `package.json` at the repo root by default. When the frontend lives in a subdirectory, set `package_json_file: frontend/package.json` explicitly. Same pitfall likely applies to any action that reads a project-level config file.

## 2026-06-15
- Narrowed `_with_cache` ASGI wrapper from `2xx/3xx` to `2xx` only — if a redirect (3xx) were ever emitted from the `/assets/` StaticFiles mount, it would get cached for a year with `immutable`, which is incorrect. The mount only serves flat hashed files so this is currently theoretical, but the guard prevents a subtle caching bug if StaticFiles routing changes.
