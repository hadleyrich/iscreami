# Sentinel — Security Patrol Log

## 2026-07-03
- Added `Permissions-Policy` header to security middleware, disabling unused
  browser APIs (geolocation, camera, mic, payment, USB, serial, bluetooth, etc.)
  — opened PR #66

## 2026-07-04
- Added `max_length` constraints to unbounded string fields (name, description,
  source, recipe_type) and `gt=0` to `serving_size_g` to prevent resource-exhaustion
  via unbounded inputs — opened PR #74

## 2026-07-05
- Capped imported recipes at 200 and ingredients at 100 per recipe in
  `/recipes/import` (bypassed Pydantic validation) to prevent
  resource-exhaustion DoS — opened PR #78

## 2026-06-19
- Added `max_length=100` to `CalculateRequest.ingredients`, `RecipeCreate.ingredients`,
  and `RecipeUpdate.ingredients` to prevent resource-exhaustion DoS via unbounded
  ingredient arrays — opened PR #39

## 2026-06-15
- Replaced `'unsafe-inline'` in CSP `script-src` with SHA-256 hash of the only
  inline script (anti-FOUC theme script), eliminating CSP bypass — opened PR #28

## 2026-06-14
- Fixed unchecked file upload size in `/recipes/import` — `file.size` being `None` bypassed 5MB limit, enabling memory-exhaustion DoS — opened PR #22

## 2026-06-12
- Added security headers middleware (CSP, XFO, XCTO, Referrer-Policy) to FastAPI app — opened PR #13

## 2026-07-10
- Skipped — already 2+ open PRs from me on this repo (#83 CORS, #88 HSTS)

## 2026-07-14
- Skipped — still 2 open PRs from me (#83 CORS wildcard credential leak, #88 HSTS). Nothing new to patrol.
