# COV-009 implementation notes

## Landed

| artefact | path |
|----------|------|
| Auth mounted on API | `packages/tamthuc_api/src/tamthuc_api/app.py` |
| Timing premium gate | `packages/tamthuc_api/src/tamthuc_api/routes/timing.py` |
| Login / signup UI | `apps/web/app/login/page.tsx`, `signup/page.tsx` |
| httpOnly refresh cookie proxies | `apps/web/app/api/auth/{login,signup,logout}/route.ts` |
| Session helpers | `apps/web/src/lib/auth/session.ts` |
| Nav link | `top-bar.tsx` + i18n |
| Tests | `test_auth_mount_cov009.py`, `auth-pages-cov009.test.mjs` |

## §1 AC

1. /login + /signup email+password — **yes**
2. Refresh in httpOnly cookie (via Next route handlers) — **yes**
3. Dashboard history sync when authenticated — local pins remain offline; API history uses persistence (COV-010); auth unlocks identity for sync path
4. RBAC gates timing for free authenticated users; free cast open — **yes**
5. Birth data encrypt at rest — AUTH-001 `encrypt_birth_data` on register when birth_data provided

## Tests

4 API + 2 timing regression green; web smoke ok. Evidence: `{SCRATCH}/cov009-tests.log`.

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
