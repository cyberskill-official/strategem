---
id: FR-API-004
title: "Persistence and audit - step 9 of the query flow: persist the query, the cast chart(s), the detected patterns, and the report into the PLAT-003 tables, and write an audit_logs row for every sensitive action; the chart is stored as the engine's la so envelope, never re-derived"
module: API
priority: MUST
status: done
phase: P0
slice: 1
lang: python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-46, strategy 4.2, strategy 4.4]
related_frs: [FR-API-001, FR-PLAT-003, FR-AUTH-001, FR-AUTH-002, FR-RAG-004, FR-REPORT-001, FR-LEGAL-002]
depends_on: [FR-API-001, FR-PLAT-003]
blocks: []
new_paths:
  - packages/tamthuc_api/tamthuc_api/persistence.py
  - packages/tamthuc_api/tamthuc_api/audit.py
  - packages/tamthuc_api/tamthuc_api/repositories.py
  - packages/tamthuc_api/tests/test_persistence.py
  - packages/tamthuc_api/tests/test_audit.py
---

## §1 - Description (BCP-14 normative)

This FR implements step 9 of the query flow: persisting the query, the cast chart(s), the detected patterns, and the generated report, and writing an audit row for every sensitive action. It extends the `tamthuc_api` package. It owns the write path and the repository layer over the FR-PLAT-003 tables; it does NOT own the table migrations or RLS (FR-PLAT-003) nor the human-review queue (FR-RAG-004), though its audit rows feed both.

Persistence SHALL write into the tables FR-PLAT-003 provisions (Grok-46 schema): `queries(id, user_id, query_type, input_data, systems_used, created_at)`, `charts(id, query_id, system, chart_data, patterns_detected, created_at)`, and `reports(id, query_id, report_data, pdf_path, generated_at)`. The `charts.chart_data` column SHALL store the engine's la so JSON envelope (FR-PLAT-002) exactly as cast, and `charts.patterns_detected` SHALL store the FR-RULE-003 output; this FR SHALL NOT re-derive or normalize any chart field, preserving the read-only invariant end to end (strategy 4.3, 4.4). A single query with multiple systems SHALL produce one `queries` row and one `charts` row per system, all sharing the `query_id`.

Auditing SHALL write an `audit_logs(id, user_id, action, details, created_at)` row for every sensitive action: any read or write of `birth_data`, a chart cast on behalf of a user, a report generation or download, a tier change, an authentication event of note (login, refresh, social link), a DSAR export or erasure (FR-AUTH-004), and any abuse action (FR-API-003). Audit rows SHALL be append-only and SHALL NOT contain plaintext `birth_data` or full question text - they record that an action occurred, by whom, and enough context to investigate, not the sensitive payload itself. Writes SHALL be transactional with the request outcome: a failed persistence SHALL NOT silently drop a served response, and a served response SHALL have its audit row (the audit write is part of completing the request, not a fire-and-forget afterthought).

## §2 - Why this design (rationale for humans)

Step 9 is where the platform becomes accountable. Persisting the query, chart, patterns, and report gives the user their history, gives the product its reproducibility (a stored la so envelope plus its flags re-casts to the same chart), and gives the eval loop and human review their raw material. Storing the chart as the exact engine envelope, never a re-serialized copy, is the same read-only discipline the gateway enforces in flight, now enforced at rest: the database holds what the engine produced, so a stored chart is auditable against the deterministic oracle (RISK-8).

Audit is a legal and safety obligation, not a log nicety. The product handles birth data and question text, which are sensitive personal data under VN PDPD and GDPR (strategy 4.4, RISK-5), and the platform's whole positioning depends on being able to show who did what with that data (strategy 7). The two rules that make audit trustworthy are that it is append-only (you cannot quietly rewrite the record) and that it records the fact of an action without copying the sensitive payload into a second, less-protected place - an audit table full of plaintext birth data would be a new breach surface, not a control. Making the audit write part of request completion, rather than a best-effort side effect, is what keeps the trail complete when it matters.

## §3 - Contract (schema / repositories / audit)

### Tables written (FR-PLAT-003 owns the DDL; this FR writes them)

| Table | Columns (Grok-46) | This FR writes |
|---|---|---|
| queries | id, user_id, query_type, input_data jsonb, systems_used text[], created_at | one row per query |
| charts | id, query_id, system, chart_data jsonb, patterns_detected jsonb, created_at | one row per system |
| reports | id, query_id, report_data jsonb, pdf_path, generated_at | one row per generated report |
| audit_logs | id, user_id, action, details jsonb, created_at | one row per sensitive action |

`charts.chart_data` is the FR-PLAT-002 envelope verbatim; `input_data` holds the `QueryRequest` minus any secret; `systems_used` mirrors the requested systems.

### Repositories (`tamthuc_api/repositories.py`, `persistence.py`)

```python
class QueryRepo(Protocol):
    async def create(self, user_id: str, req: QueryRequest) -> str: ...          # -> query_id
class ChartRepo(Protocol):
    async def create(self, query_id: str, system: str,
                     chart: LaSo, patterns: list[CachCuc]) -> str: ...           # stores envelope verbatim
class ReportRepo(Protocol):
    async def create(self, query_id: str, report_data: dict, pdf_path: str | None) -> str: ...
    async def get(self, report_id: str, user_id: str) -> Report | None: ...      # RLS-scoped read

async def persist_query_result(user_id: str, req: QueryRequest,
                               charts: list[LaSo], patterns: list[CachCuc],
                               report: dict | None) -> PersistResult:
    # one queries row + one charts row per system (+ report row) in a single transaction
```

### Audit (`tamthuc_api/audit.py`)

```python
class AuditAction(str, Enum):
    birth_data_read = "birth_data_read"; birth_data_write = "birth_data_write"
    chart_cast = "chart_cast"; report_generate = "report_generate"; report_download = "report_download"
    tier_change = "tier_change"; auth_login = "auth_login"; auth_refresh = "auth_refresh"
    dsar_export = "dsar_export"; dsar_erase = "dsar_erase"; abuse_action = "abuse_action"

async def audit(user_id: str | None, action: AuditAction, details: dict) -> None:
    # append-only insert into audit_logs; details carries context, NEVER plaintext birth_data or full question text
```

## §4 - Acceptance criteria

1. A single-system query persists one `queries` row and one `charts` row; a multi-system `/calculate/all` query persists one `queries` row and one `charts` row per system, all sharing the `query_id`.
2. `charts.chart_data` equals the engine's la so envelope byte-for-byte (no re-derivation); a round-trip test re-reads it and re-casts to an identical chart from `dau_vao` plus flags.
3. Every sensitive action writes exactly one `audit_logs` row with the correct `AuditAction`, the acting `user_id` (or null for anonymous/abuse), and a `details` object that contains no plaintext `birth_data` and no full question text.
4. Persistence and the served response are transactional: an injected DB failure on the write does not return a 200 with lost data; the request fails with the FR-API-001 error envelope and no partial rows remain.
5. `ReportRepo.get` honors row-level security (FR-PLAT-003): a user cannot read another user's report; a cross-user read returns 404, not another user's data.
6. Audit rows are append-only: an attempt to update or delete an audit row is rejected (enforced by FR-PLAT-003 grants); a test asserts the write-only contract at the repository layer.

## §5 - Verification

- `tests/test_persistence.py`: single- and multi-system row counts and shared `query_id`; the byte-identical `chart_data` and the re-cast round-trip; the transactional failure case (no partial persistence, no silent 200); RLS-scoped report read.
- `tests/test_audit.py`: one row per sensitive action with the right `AuditAction`; the no-plaintext-sensitive-data assertion on `details`; the append-only contract; audit emitted for abuse actions (FR-API-003) and auth events (FR-AUTH-001).
- Integration: the orchestrator's step 9 calls `persist_query_result` and `audit`; a served query is followed by its persisted rows and its `chart_cast` audit row.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_api`, `pytest packages/tamthuc_api` (the DB path runs behind a marker when a test Postgres is present; a fake repo covers the default suite).

## §6 - Implementation skeleton

1. `repositories.py`: `QueryRepo` / `ChartRepo` / `ReportRepo` protocols with a Postgres implementation over the FR-PLAT-003 tables and an in-memory fake for tests.
2. `persistence.py`: `persist_query_result` writing the query, per-system charts, and report in one transaction; the re-cast round-trip helper.
3. `audit.py`: the `AuditAction` enum and the append-only `audit` writer with the sensitive-data redaction rule.
4. Wire step 9 of the FR-API-001 orchestrator to `persist_query_result` + `audit`; wire abuse and auth audit calls from FR-API-003 / FR-AUTH-001.

## §7 - Dependencies

Depends on FR-API-001 (the orchestrator whose step 9 this completes, and the error envelope a failed write returns) and FR-PLAT-003 (the physical `queries` / `charts` / `reports` / `audit_logs` tables, their indexes, and the RLS this write path relies on). Stores the FR-PLAT-002 la so envelope verbatim and the FR-RULE-003 patterns. Its audit rows feed FR-RAG-004 (human-review context), FR-AUTH-004 (DSAR export reads the user's persisted history; erasure removes it), and FR-LEGAL-002 (retention and disclosure operate on exactly these tables). Auth and abuse events audited here originate in FR-AUTH-001 and FR-API-003.

## §8 - Example payloads

```json
// queries row (input_data mirrors the QueryRequest, minus secrets)
{ "id": "q_...", "user_id": "u_...", "query_type": "trach_thoi",
  "input_data": { "datetime": "2004-01-01T10:30:00", "tz": "+07:00", "kinh_do": 105.85, "systems": ["qimen"] },
  "systems_used": ["qimen"], "created_at": "2026-07-08T12:00:00Z" }
```

```json
// audit_logs row - records the fact, not the sensitive payload
{ "id": "a_...", "user_id": "u_...", "action": "birth_data_read",
  "details": { "purpose": "chart_cast", "query_id": "q_...", "fields": ["date","time","place"] },
  "created_at": "2026-07-08T12:00:00Z" }
```

## §9 - Open questions

- Whether `charts.patterns_detected` duplicates the envelope's `cach_cuc` or is stored separately. Default: store the FR-RULE-003 match output in `patterns_detected` (it carries match scores and the `(id, version)` stamps), while `chart_data.cach_cuc` holds the engine's own list; a test asserts they reconcile. Revisit if the duplication proves noisy.
- Retention windows per table. Default: this FR persists; FR-LEGAL-002 sets the retention and the erasure contract over these tables, and FR-AUTH-004 executes DSAR against them. Keep the windows in the LEGAL config, not hardcoded here.
- Audit sink: same Postgres vs a separate append-only store. Default: the `audit_logs` table in the shared Postgres with delete/update revoked (FR-PLAT-003 grants); a dedicated immutable sink is a later hardening step (FR-PLAT-007) that keeps the same `audit` interface.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Chart re-derived at rest | `chart_data` re-serialized/normalized instead of stored verbatim | forbidden; store the envelope byte-for-byte; the re-cast round-trip test fails on any change |
| Sensitive data in audit | plaintext birth_data or full question text in `audit_logs.details` | redaction rule strips it; a test asserts `details` never carries the sensitive payload |
| Silent data loss | write fails but a 200 is returned | persistence is transactional with the response; a failed write yields the error envelope, no partial rows |
| Mutable audit trail | an audit row updated or deleted | append-only; DB grants revoke update/delete (FR-PLAT-003); repository exposes no mutator |
| Cross-user read | one user reads another's chart/report | RLS on the tables; report read is user-scoped; a cross-user read returns 404 |
| Missing audit on served action | a sensitive action completes without an audit row | audit is part of request completion, not fire-and-forget; integration test pairs each action with its row |

## §11 - Notes

This FR closes the query flow and makes the platform accountable: it stores what the engine produced (never a re-derivation) and records who touched sensitive data (never by copying it). The two disciplines to hold are verbatim chart storage and append-only, payload-free audit. It extends the same `tamthuc_api` app as FR-API-001/002/003, writing into the FR-PLAT-003 schema, so the gateway remains one installable, mypy-clean unit. Retention, export, and erasure over these tables belong to FR-LEGAL-002 and FR-AUTH-004; this FR gives them a clean, audited store to operate on.
