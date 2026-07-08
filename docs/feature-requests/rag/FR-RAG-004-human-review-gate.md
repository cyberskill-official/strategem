---
id: FR-RAG-004
title: "HumanReviewGate pipeline - a review queue for AI interpretations flagged important/low-confidence, approve/reject with a required reason + audit, gate before the interpretation reaches the user, review_status back on the AIDisclosure; owns the review policy RAG-003 sets requires_human_review from"
module: RAG
priority: MUST
status: ready_to_implement
phase: P1
slice: 1
lang: python
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s4.3, strategy 4.4, strategy 8]
related_frs: [FR-RAG-003, FR-KB-004, FR-WEB-001, FR-WEB-003, FR-AUTH-002, FR-PLAT-003, FR-API-004]
depends_on: [FR-RAG-003]
blocks: []
new_paths:
  - packages/tamthuc_rag/tamthuc_rag/review/__init__.py
  - packages/tamthuc_rag/tamthuc_rag/review/gate.py
  - packages/tamthuc_rag/tamthuc_rag/review/queue.py
  - packages/tamthuc_rag/tamthuc_rag/review/policy.py
  - packages/tamthuc_rag/tamthuc_rag/review/models.py
  - packages/tamthuc_rag/migrations/0001_review_queue.sql
  - packages/tamthuc_rag/tests/test_review_gate.py
  - packages/tamthuc_rag/tests/fixtures/review_tickets.json
  - docs/contracts/review-ticket.schema.json
---

## §1 - Description (BCP-14 normative)

This FR is the runtime human-in-the-loop for interpretation: a review queue that intercepts AI interpretations flagged important or low-confidence, holds them for an expert to approve or reject with a reason, and gates them before they reach the user. It is the operational form of the third anti-hallucination layer (human-in-the-loop) that FR-RAG-003 declares (Claude-06 s4.3; strategy 4.4). It consumes the `requires_human_review` flag and the `AIDisclosure` that FR-RAG-003 produces, and it owns the review policy that FR-RAG-003 consults to set that flag.

When an `Interpretation` has `requires_human_review = false`, the gate SHALL release it, set `disclosure.review_status = "not_required"`, and let it reach the user unchanged. When `requires_human_review = true`, the gate SHALL NOT release the interpretation to the user; it SHALL enqueue a `ReviewTicket`, set `disclosure.review_status = "pending"`, and return a withheld view that carries no confident uncited claims. A reviewer holding the review role (FR-AUTH-002) SHALL approve or reject each ticket with a non-empty `reason`; the decision SHALL be recorded immutably with the reviewer id and timestamp (an audit row). On approve, the gate SHALL set `review_status = "approved"` and release the interpretation (with the reviewer's optional edits to the interpretation text and recommendations only); on reject, it SHALL set `review_status = "rejected"`, withhold the interpretation, and surface a safe under-review message instead of the raw AI text.

The gate SHALL own the `ReviewPolicy` - the confidence threshold and the high-stakes question-type set - that FR-RAG-003's guard reads to decide `requires_human_review`, so the flag and the queue share one policy. The gate SHALL NOT touch the la so envelope: it operates only on the `Interpretation` object and the review record, and it SHALL NEVER write `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai` (strategy 4.3). A reviewer edit SHALL change only the interpretation text, recommendations, and citations shown, never the chart the engine cast, and the `AIDisclosure` SHALL be preserved with only `review_status` updated. Every interpretation that reaches the user SHALL carry an `AIDisclosure` whose `review_status` is one of `not_required` or `approved`; a `pending` or `rejected` interpretation SHALL never be presented as a finished reading.

## §2 - Why this design (rationale for humans)

The three anti-hallucination layers only work if the third one is real: citation-required and retrieval-only keep the model honest about its sources, but for a consequential judgment a person still has to be able to catch a reading that is technically cited yet wrong, misleading, or over-confident for the stakes (Claude-06 s4.3). A HumanReviewGate is where that person stands. Without it, "human-in-the-loop" is a slogan; with it, an interpretation flagged low-confidence or high-stakes physically cannot reach the user until a reviewer has looked at it and said yes. For a heritage subject under VN law, that is also the difference between decision-support education and unsupervised fortune-telling for profit (strategy 7, RISK-3, RISK-4): the gate is the control that keeps consequential output from going out unattended.

Owning the policy here, rather than scattering thresholds across the interpreter, is what keeps the flag and the queue in agreement. FR-RAG-003 sets `requires_human_review` by asking this FR's policy; this FR then queues exactly the interpretations it flagged, so there is no case where the interpreter thinks a reading is fine but the gate would have caught it, or vice versa. The withheld view is a small but load-bearing detail: while a reading is pending or after it is rejected, the user must not see the raw AI text, because that text is precisely what has not yet been trusted; showing a neutral under-review state instead is the honest interface for "we are not confident enough to show this yet". Keeping the gate off the la so envelope is the same architectural boundary the whole platform rests on - a reviewer improves the words, never the chart, because the chart is the deterministic engine's and is reproducible from its inputs and flags (strategy 4.3).

## §3 - Contract (policy, models, queue, gate)

### Review policy (`tamthuc_rag/review/policy.py`)

```python
class ReviewPolicy(BaseModel):
    confidence_threshold: float = 0.55        # below this -> requires review
    high_stakes_question_types: set[str] = {  # always review regardless of confidence
        "suc_khoe", "phap_ly", "tai_chinh_lon", "hon_nhan_dai_su" }
    def requires_review(self, confidence: float, question_type: str) -> bool:
        return confidence < self.confidence_threshold or question_type in self.high_stakes_question_types
```

FR-RAG-003's `guard.enforce` calls `ReviewPolicy.requires_review(...)` to set `requires_human_review`; this FR is the single owner of the policy so the flag and the queue cannot disagree.

### Ticket and outcome (`tamthuc_rag/review/models.py`)

```python
class ReviewStatus(str, Enum):
    not_required = "not_required"; pending = "pending"; approved = "approved"; rejected = "rejected"

class ReviewTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    query_id: str
    interpretation_id: str              # the persisted interpretation (FR-API-004)
    persona_level: str
    confidence: float
    reason_flagged: str                 # "low_confidence" | "high_stakes:<type>"
    status: ReviewStatus
    interpretation: dict                # snapshot for the reviewer (FR-RAG-003 Interpretation)
    disclosure: dict                    # the AIDisclosure snapshot
    created_at: datetime

class ReviewOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ticket_id: str
    reviewer_id: str                    # holds the review role (FR-AUTH-002)
    decision: Literal["approve", "reject"]
    reason: str                         # required, non-empty
    edited_interpretation: dict | None  # optional reviewer correction (text/recs/citations only)
    decided_at: datetime
```

### Queue (`tamthuc_rag/review/queue.py`)

```python
class ReviewQueue(Protocol):
    def enqueue(self, interp: Interpretation, query_id: str, reason: str) -> ReviewTicket: ...
    def pending(self, limit: int = 50) -> list[ReviewTicket]: ...
    def get(self, ticket_id: str) -> ReviewTicket | None: ...
    def decide(self, ticket_id: str, reviewer_id: str,
               decision: Literal["approve", "reject"], reason: str,
               edited_interpretation: dict | None = None) -> ReviewTicket: ...

class RelationalReviewQueue:   # default: review_ticket + review_outcome in the shared Postgres
    ...
class InMemoryReviewQueue:     # tests
    ...
```

`decide` SHALL require the review role and a non-empty reason, update `review_status`, persist the outcome immutably, and write an audit row.

### Gate (`tamthuc_rag/review/gate.py`)

```python
class GateResult(BaseModel):
    released: bool
    interpretation: dict | None    # the releasable interpretation when released; else None
    ticket_id: str | None          # set when withheld for review
    withheld_view: dict | None     # safe under-review payload for the UI when not released

def gate(interp: Interpretation, query_id: str, queue: ReviewQueue) -> GateResult:
    if not interp.requires_human_review:
        interp.disclosure.review_status = "not_required"
        return GateResult(released=True, interpretation=interp.model_dump())
    ticket = queue.enqueue(interp, query_id, reason=flag_reason(interp))
    interp.disclosure.review_status = "pending"
    return GateResult(released=False, ticket_id=ticket.id, withheld_view=under_review_view(interp))

def apply_outcome(ticket: ReviewTicket, outcome: ReviewOutcome) -> GateResult:
    # approve: review_status=approved; release (with edited text/recs/citations if provided); audit
    # reject:  review_status=rejected; withhold; return the safe under-review view; audit
```

`under_review_view` strips confident claims and shows a neutral "awaiting expert review" state; it is what FR-WEB-001's `HumanReviewGate` component renders. `apply_outcome` mutates only the interpretation's text, recommendations, and citations on an approved edit; it never mutates the chart fields, and it refreshes only `disclosure.review_status`.

## §4 - Acceptance criteria

1. An interpretation with `requires_human_review = false` is released unchanged with `review_status = "not_required"`.
2. An interpretation with `requires_human_review = true` is withheld: a `ReviewTicket` is enqueued, `review_status = "pending"`, and the returned `withheld_view` contains no confident uncited claims (not the raw AI text).
3. `decide` requires the review role and a non-empty reason; a decision by a non-reviewer or with an empty reason is rejected for both approve and reject.
4. On approve, `review_status = "approved"` and the interpretation is released; a reviewer edit changes only interpretation text / recommendations / citations, and a byte-equality check shows the la so envelope and the chart `cach_cuc` are untouched.
5. On reject, `review_status = "rejected"`, the interpretation is withheld, and the user-facing result is the safe under-review view, never the rejected AI text.
6. `ReviewPolicy.requires_review` drives FR-RAG-003's flag: a low-confidence or high-stakes case flags and queues; a confident low-stakes case does not - the flag and the queue agree by construction.
7. Every decision writes an immutable audit row (reviewer, ticket, decision, reason, timestamp); no interpretation with `review_status` in {`pending`, `rejected`} is ever presented as finished.

## §5 - Verification

- `tests/test_review_gate.py`: the not-required release path; the pending-withhold path with the stripped `withheld_view`; the role guard and required-reason guard; approve-with-edit asserting the la so and `cach_cuc` are byte-identical before and after (read-only invariant); reject producing the safe view; the policy-drives-flag parity with a FR-RAG-003 stub; audit-row-per-decision.
- Contract: `ReviewTicket` / `ReviewOutcome` validate against `docs/contracts/review-ticket.schema.json`; Pydantic/JSON-Schema parity in CI; `AIDisclosure.review_status` transitions are asserted (`pending -> approved | rejected`, `not_required` terminal).
- Backend parity: run the lifecycle through the `RelationalReviewQueue` (test Postgres or fake) and the `InMemoryReviewQueue`; assert identical `pending` / `get` results.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_rag`, `pytest packages/tamthuc_rag` (default in-memory; the Postgres path behind a marker).

## §6 - Implementation skeleton

1. `review/policy.py`: the `ReviewPolicy` (threshold + high-stakes types) that FR-RAG-003 consults; a default config plus an override hook.
2. `review/models.py`: `ReviewTicket`, `ReviewOutcome`, `ReviewStatus`; author `docs/contracts/review-ticket.schema.json`.
3. `review/queue.py`: the `ReviewQueue` protocol, `RelationalReviewQueue`, `InMemoryReviewQueue`; `migrations/0001_review_queue.sql` (`review_ticket` + immutable `review_outcome` + audit).
4. `review/gate.py`: `gate` (release vs withhold), `apply_outcome` (approve/reject), `under_review_view` (safe payload), the read-only-envelope guard on reviewer edits.
5. Wire the role check to FR-AUTH-002 and the `withheld_view` shape to FR-WEB-001's `HumanReviewGate` component.

## §7 - Dependencies

Depends on FR-RAG-003 (which produces the `Interpretation`, the `requires_human_review` flag, and the `AIDisclosure` this gate consumes; this FR in turn owns the `ReviewPolicy` FR-RAG-003 reads). Uses FR-AUTH-002 for the reviewer role, FR-PLAT-003 for the `review_ticket` / `review_outcome` tables and audit rows (soft edge; applied through the PLAT runner), and FR-API-004 for the persisted interpretation the ticket references. Surfaced by FR-WEB-001 (the `HumanReviewGate` component) and FR-WEB-003 (the results screen, which shows the under-review state instead of a pending reading). Blocks nothing in the catalog, but it is the runtime gate every AI-facing surface passes flagged output through. Sibling to FR-KB-004: same human-in-the-loop principle at a different stage (AI interpretations at query time here, knowledge content at curation time there).

## §8 - Example payloads

```json
// a ReviewTicket for a high-stakes flagged interpretation
{ "id": "tkt_00042", "query_id": "q_9931", "interpretation_id": "interp_5521",
  "persona_level": "beginner", "confidence": 0.48, "reason_flagged": "high_stakes:phap_ly",
  "status": "pending", "created_at": "2026-07-08T12:05:00Z",
  "interpretation": { "beginner_interpretation": "...", "citations": ["yba_dieu_012"], "confidence": 0.48 },
  "disclosure": { "is_ai_generated": true, "model": "gpt-4o-mini", "prompt_version": "sys-1.0.0",
    "retrieved_citation_ids": ["yba_dieu_012"], "review_status": "pending" } }
```

```json
// the reviewer's approve outcome (reason required; edits touch text/recs only)
{ "ticket_id": "tkt_00042", "reviewer_id": "master_tue", "decision": "approve",
  "reason": "Cited grounding is correct; softened the legal-adjacent phrasing to decision-support framing.",
  "edited_interpretation": { "beginner_interpretation": "...softened...", "citations": ["yba_dieu_012"] },
  "decided_at": "2026-07-08T12:40:00Z" }
```

## §9 - Open questions

- The exact confidence threshold and the high-stakes question-type set. Default: a conservative threshold (0.55) plus a health/legal/large-financial/major-life allowlist; tune from review outcomes and FR-RAG-006 evidence, keeping the policy in one place so FR-RAG-003's flag follows.
- What the user sees while pending: a neutral "awaiting expert review" state versus a partial reading. Default: neutral under-review view with no confident claims; a partial cited summary only if review latency proves too slow, and only content that already passed the citation guard.
- Whether reject offers the user a rule-based fallback reading. Default: show the safe under-review message at MVP; wiring the FR-RAG-007 degraded reading in on reject is a follow-up once both exist.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Flagged reading leaks | a `requires_human_review` interpretation reaches the user | gate withholds; only `not_required` or `approved` interpretations are presented |
| Reasonless decision | approve/reject with an empty reason | rejected; a non-empty reason is required for both outcomes |
| Unauthorized reviewer | a non-review role decides | rejected; only the FR-AUTH-002 review role may decide |
| Reviewer edits the chart | an edit mutates `ban`/`cach_cuc` | impossible: edits touch only interpretation text/recs/citations; byte-equality test on the envelope |
| Flag/queue disagreement | interpreter flags differ from what is queued | one `ReviewPolicy` owned here drives both; parity test |
| Raw rejected text shown | rejected AI text surfaced to the user | rejected -> withheld + safe view; the raw text never renders |
| Missing/rewritten disclosure | output without a truthful `review_status` | gate always sets `review_status`; only that field changes; schema requires the disclosure |

## §11 - Notes

This FR makes the third anti-hallucination layer operational, and its whole reason to exist is that a consequential reading must not reach a user unattended. Two invariants are non-negotiable and mirror FR-RAG-003: the gate reads the interpretation and never writes the la so, and no interpretation reaches the user without a truthful `review_status` on its `AIDisclosure`. Keep the `ReviewPolicy` here as the single source so the flag FR-RAG-003 sets and the queue this FR runs can never drift. It is a deliberate sibling of FR-KB-004, not a merge - different objects, different review focus, same principle (strategy 4.4). The package `tamthuc_rag` is shared with FR-RAG-001/002/003/005/006/007; this FR adds the `review/` module, so the RAG branch stays one installable, mypy-clean unit.
