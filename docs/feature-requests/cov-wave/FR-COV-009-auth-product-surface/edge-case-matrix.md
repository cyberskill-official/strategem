# edge-case-matrix@1 — COV-009

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | HAPPY | register + login + me | 200 tokens + email | test_auth_register_login_me |
| E2 | FREE | cast without auth | 200 chart | test_free_cast_without_auth |
| E3 | RBAC | free user timing | 403 FORBIDDEN_TIER | test_timing_gated_for_free_authenticated |
| E4 | DEGRADATION | anonymous timing | 200 windows (local open) | test_timing_open_anonymous |
| E5 | SECURITY | refresh httpOnly cookie | Set-Cookie httpOnly | auth-pages-cov009.test.mjs |
| E6 | WEB | /login /signup pages | testids present | auth-pages-cov009.test.mjs |
| E7 | CRYPTO | birth data encrypt | AUTH-001 service path | packages/tamthuc_auth tests |
| E8 | SESSION | logout clears cookie | maxAge 0 | logout route |
