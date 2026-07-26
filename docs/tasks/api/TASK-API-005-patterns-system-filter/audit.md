---
task_id: TASK-API-005
audited: 2026-07-27
verdict: PASS (after revision)
score_pre_revision: 7/10
score_post_expansion: 9/10
score_post_revision: 10/10
issues_resolved: 6
template: engineering-spec@1
---

## §1 - Verdict summary

Compact improvement spec (~220 lines): 6 normative §1 clauses, 8 ACs, 10 failure-mode rows, concrete verification commands. Grounded in the 2026-07-25 live-truth-audit finding plus a same-day 2026-07-27 prod re-probe showing the handler already filters — scope correctly framed as contract lock / acceptance hardening rather than a fake greenfield bug.

## §2 - Findings (all resolved)

### ISS-001 — Scope honesty vs live probe
Risk of authoring a "fix ignored filter" task while prod already returns 105/175 for `system=qimen`. Resolved: §1 re-verify note + §11 state remaining work (smoke/OpenAPI/UI/audit annotation); type stays `improvement` / class `improvement`.

### ISS-002 — Smoke false green
`smoke-prod-full.sh` logged filter success without asserting `system` or subset totals. Resolved: §1 #4 + AC #5 + §3 smoke contract require hard-fail asserts.

### ISS-003 — Alias / unknown paths underspecified
Only english `system=` was implied. Resolved: §1 #1–#2, AC #2–#4, and dedicated unit tests in §5.

### ISS-004 — OpenAPI gap
`openapi-v1.md` omitted the patterns route entirely. Resolved: §1 #3 + AC #6 + §6 step 4.

### ISS-005 — Audit finding closure without trail
Closing a deferred audit bullet by deletion would erase history. Resolved: §1 #6 + AC #7 require dated remediation annotation citing TASK-API-005.

### ISS-006 — UI vs API param name drift
Browse page still sends `he=`. Resolved: §1 #5 + AC #8 allow alias but SHOULD migrate to `system=`; §6 step 5.

## §3 - Resolution

All 6 mechanical concerns addressed. **Score = 10/10.**

---

*End of TASK-API-005 audit.*
