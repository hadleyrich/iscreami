# Sentinel — Security Patrol Findings

## 2026-06-15
- Replaced `'unsafe-inline'` in CSP `script-src` with SHA-256 hash of the only
  inline script (anti-FOUC theme script), eliminating CSP bypass — opened PR #
