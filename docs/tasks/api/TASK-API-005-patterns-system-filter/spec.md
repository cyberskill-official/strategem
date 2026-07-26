---
id: TASK-API-005
title: "Knowledge patterns ?system= filter contract lock - honor system filter, harden smoke/OpenAPI, close live-truth-audit finding"
module: API
priority: SHOULD
status: ready_to_implement
class: improvement
phase: P1
slice: 1
lang: python
effort_h: 4
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-27
refs:
  - docs/tasks/_audits/2026-07-25-live-truth-audit.md
  - TASK-API-001
  - TASK-COV-019
related_frs: [TASK-API-001, TASK-COV-019, TASK-RULE-001]
depends_on: [TASK-API-001]
blocks: []
source_pages:
  - docs/tasks/_audits/2026-07-25-live-truth-audit.md#L19
  - packages/tamthuc_api/src/tamthuc_api/routes/knowledge.py
  - packages/tamthuc_api/tests/test_knowledge_patterns_cov019.py
  - scripts/smoke-prod-full.sh
  - "prod probe 2026-07-27: GET https://api.strategem.cyberskill.world/api/v1/knowledge/patterns?system=qimen → total 105 of 175, systems=['qimen']"
new_paths:
  - docs/contracts/openapi-v1.md
modified_paths:
  - packages/tamthuc_api/src/tamthuc_api/routes/knowledge.py
  - packages/tamthuc_api/tests/test_knowledge_patterns_cov019.py
  - scripts/smoke-prod-full.sh
  - apps/web/app/patterns/page.tsx
  - docs/tasks/_audits/2026-07-25-live-truth-audit.md
---

## §1 - Description (BCP-14 normative)

1. `GET /api/v1/knowledge/patterns` MUST honor the `system` query parameter as the canonical filter for classical system (`qimen` | `liuren` | `taiyi`), and MUST continue to accept `he=` as an alias (including Vietnamese codes `ky_mon` / `luc_nham` / `thai_at`). When either filter is set, every returned row MUST match the requested system; `total` MUST equal the filtered set size (not the unfiltered catalog size).

2. An unknown `system` / `he` value MUST return HTTP 200 with `patterns: []` and `total: 0` (not the full catalog, not 4xx). Omitting both filters MUST return the full seeded catalog (subject to `limit`).

3. The OpenAPI sketch at `docs/contracts/openapi-v1.md` MUST document `GET /api/v1/knowledge/patterns` with query params `system`, `he`, `q`, and `limit`, stating that `system` is canonical and `he` is the alias.

4. `scripts/smoke-prod-full.sh` MUST assert the filter, not merely that the request returns 200: after `?system=qimen`, every returned row's `system` MUST be `qimen`, and filtered `total` MUST be strictly less than the unfiltered catalog `total` when the catalog contains more than one system.

5. The patterns browse UI (`apps/web/app/patterns/page.tsx`) SHOULD send `system=` when a system filter is selected (keeping `he=` acceptable as a transitional alias). Either param is valid server-side; the UI MUST NOT regress to a path that ignores the selected system.

6. When acceptance criteria in §4 pass, the deferred bullet in `docs/tasks/_audits/2026-07-25-live-truth-audit.md` that claims `?system=` ignores the filter MUST be marked remediated with a dated note citing this task — not silently deleted without a trail.

### Re-verify note (authoring session 2026-07-27)

Live prod already filters correctly (`total` 175 unfiltered → 105 `qimen` / 40 `liuren` / 30 `taiyi`; aliases `ky_mon` work). Handler + unit test `test_filter_by_system_query_param` exist on `main`. This task is therefore a **contract lock + acceptance hardening** improvement: close the audit finding, strengthen smoke/OpenAPI/UI alignment, and prevent regression — not a greenfield filter implementation.

## §2 - Why this design (rationale for humans)

**Why keep `he=` as alias (§1 #1)?** TASK-COV-019 and the browse UI shipped with `he=`; TASK-API-001's contract names `?system=`. Dual acceptance avoids breaking the live UI while making the documented API name work. Canonicalizing on `system` matches the la so / engine vocabulary used elsewhere in the gateway.

**Why empty-set for unknown system (§1 #2)?** Returning the full catalog on a typo reintroduced the 2026-07-25 live-audit defect class ("filter ignored"). Empty is the honest answer and is cheap to assert.

**Why strengthen smoke (§1 #4)?** Today's smoke logs `patterns filter system=…` without failing when the first row is missing or wrong-system. Unit tests alone did not catch the pre-fix prod path; smoke must guard deploy drift.

**Why UI SHOULD prefer `system=` (§1 #5)?** Keeps the product surface and the OpenAPI name aligned so the next live audit does not re-flag a "works via alias only" gap as a contract miss.

## §3 - Contract (endpoint / filter / smoke)

### Response shape (unchanged)

```json
{
  "patterns": [ { "id": "...", "system": "qimen", "he": "ky_mon", "name": "...", "...": "..." } ],
  "total": 105,
  "source": "tamthuc_kb.seed"
}
```

### Filter resolution (`packages/tamthuc_api/.../routes/knowledge.py`)

```python
he_n = (system or he or "").strip().lower()
# alias map: ky_mon→qimen, luc_nham→liuren, thai_at→taiyi (+ english ids)
# rows kept only when r.system == want OR r.he == he_n
```

### OpenAPI addition (`docs/contracts/openapi-v1.md`)

Document:

- `GET /api/v1/knowledge/patterns?system=&he=&q=&limit=`
- `system` canonical; `he` alias; both optional; `limit` 1..500 default 200

### Smoke assertion (`scripts/smoke-prod-full.sh`)

After unfiltered `total=T0` and filtered `?system=qimen` body:

1. HTTP 200
2. every `patterns[i].system == "qimen"` (or empty list only if catalog has zero qimen — not the case for seed ≥150)
3. `total < T0` when `T0` spans multiple systems

## §4 - Acceptance criteria

1. **System filter subsets** — `GET .../patterns?system=qimen&limit=500` returns `total` strictly less than unfiltered `total`, and every row has `system == "qimen"`.
2. **Alias parity** — `?system=ky_mon` and `?he=qimen` return the same `total` and the same system set as `?system=qimen`.
3. **Cross-system exclusion** — `?system=liuren` rows are all `liuren`; none are `qimen` or `taiyi`.
4. **Unknown system empty** — `?system=nope` returns `patterns: []` and `total: 0`.
5. **Smoke hard-fail** — `scripts/smoke-prod-full.sh` fails if filtered rows violate §4 #1 (not a soft `pass` log).
6. **OpenAPI lists the route** — `docs/contracts/openapi-v1.md` names `GET /api/v1/knowledge/patterns` and the four query params.
7. **Audit trail closed** — live-truth-audit deferred bullet for `?system=` is marked remediated with task id + date.
8. **UI filter still works** — selecting Kỳ Môn / Lục Nhâm / Thái Ất on `/patterns` loads a system-consistent list (via `system=` or still-supported `he=`).

## §5 - Verification

```bash
# unit (must stay green; extend for aliases + unknown)
cd packages/tamthuc_api && uv run pytest tests/test_knowledge_patterns_cov019.py -q

# prod / staging smoke (API_BASE required)
API_BASE=https://api.strategem.cyberskill.world bash scripts/smoke-prod-full.sh
# the patterns?system= step must FAIL if total is unfiltered or mixed systems
```

Add/extend tests in `test_knowledge_patterns_cov019.py`:

- `test_filter_by_system_query_param` (existing) — keep
- `test_system_alias_ky_mon_matches_qimen`
- `test_unknown_system_returns_empty`

Manual UI: open `/patterns`, select each system, confirm counts move and names stay in-family.

## §6 - Implementation skeleton

1. Confirm `list_patterns` already applies `system or he` (likely already true on `main`); fix only if a regression reappears.
2. Extend unit tests for aliases + unknown system.
3. Harden `smoke-prod-full.sh` assertions (compare totals; assert every row's `system`).
4. Document the route in `openapi-v1.md`.
5. Optionally switch `apps/web/app/patterns/page.tsx` from `params.set("he", he)` to `params.set("system", he)` when non-empty.
6. Annotate the live-truth-audit deferred item as remediated under TASK-API-005.

## §7 - Dependencies

- Depends on TASK-API-001 (endpoint ownership + `?system=` in the gateway contract) and the seeded catalog from TASK-RULE-001 / TASK-COV-019.
- Does not block other modules; closes a deferred live-audit finding that product truth-up waves should not re-open blindly.

## §8 - Example payloads

```http
GET /api/v1/knowledge/patterns?system=qimen&limit=500
```

```json
{
  "patterns": [
    {
      "id": "qimen_example",
      "system": "qimen",
      "he": "ky_mon",
      "name": "...",
      "meaning_modern": "Educational classical pattern note (see citations).",
      "citations": []
    }
  ],
  "total": 105,
  "source": "tamthuc_kb.seed"
}
```

```http
GET /api/v1/knowledge/patterns?system=nope&limit=500
```

```json
{ "patterns": [], "total": 0, "source": "tamthuc_kb.seed" }
```

## §9 - Open questions

All resolved for this slice:

- Canonical param name: `system` (per TASK-API-001); `he` remains alias.
- Unknown system: empty 200 (not 400) — keeps browse UX simple.
- Whether to remove `he=` later: Deferred to a future deprecation pass under TASK-API-002; out of scope here.

## §10 - Failure modes inventory

| Failure | Detection | Outcome | Recovery |
|---|---|---|---|
| `system=` ignored (full catalog) | unit + smoke total compare | fail CI / fail smoke | restore filter branch in `list_patterns` |
| Alias `ky_mon` ignored | alias unit test | fail pytest | keep alias map complete |
| Unknown system returns all | unknown-system unit test | fail pytest | empty-set branch |
| Smoke soft-pass on bad filter | hardened smoke asserts | fail smoke | fix assert + redeploy |
| OpenAPI omits route | doc review / AC #6 | task not done | add openapi lines |
| UI sends neither param when filter selected | manual / Playwright later | wrong browse UX | set `system=` in page.tsx |
| Mixed systems in filtered page | row-wise assert | fail test/smoke | fix predicate |
| Prophecy wording reintroduced | existing COV-019 blob assert | fail pytest | keep strip list |
| Deploy lag (code fixed, prod old) | smoke against prod | fail smoke | redeploy API image |
| Audit doc still claims defect after fix | AC #7 | task not done | annotate audit file |

## §11 - Implementation notes

- Prefer a minimal diff: do not refactor the KB loader or graph neighbors route in this task.
- Do not invent PayOS / counsel work here; this is a knowledge-catalog truth-up only.
- If prod probe at implement time still shows correct filter totals, still land the smoke hardening + OpenAPI + audit annotation — those are the remaining acceptance gaps.
- `backlog.yaml` W0 downgrade noise is unrelated; do not flip unrelated API-* rows to `done` as part of this task.

*End of task-API-005.*
