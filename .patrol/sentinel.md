# Sentinel — Security Patrol Log

## 2026-06-15
- Replaced `'unsafe-inline'` in CSP `script-src` with SHA-256 hash of the only
  inline script (anti-FOUC theme script), eliminating CSP bypass — opened PR #28

## 2026-06-14
- Fixed unchecked file upload size in `/recipes/import` — `file.size` being `None` bypassed 5MB limit, enabling memory-exhaustion DoS — opened PR #22

## 2026-06-12
- Added security headers middleware (CSP, XFO, XCTO, Referrer-Policy) to FastAPI app — opened PR #13
