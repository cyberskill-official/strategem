---
id: TASK-KB-004
title: "KB curation workflow - expert (master) review of patterns and classical excerpts through a review queue, accept/reject with a required reason, monotonic versioning with history, and a release gate encoding the RISK-9 expert-review-each-release process"
module: KB
priority: SHOULD
status: done
phase: P2
slice: 1
lang: python
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-24, strategy RISK-9, strategy 4.4]
related_frs: [TASK-KB-002, TASK-KB-003, TASK-RAG-004, TASK-RAG-006, TASK-AUTH-002, TASK-PLAT-003, TASK-API-004]
depends_on: [TASK-KB-002]
blocks: []
new_paths:
  - packages/tamthuc_kb/tamthuc_kb/curation/__init__.py
  - packages/tamthuc_kb/tamthuc_kb/curation/models.py
  - packages/tamthuc_kb/tamthuc_kb/curation/queue.py
  - packages/tamthuc_kb/tamthuc_kb/curation/review.py
  - packages/tamthuc_kb/tamthuc_kb/curation/release_gate.py
  - packages/tamthuc_kb/migrations/0003_curation.sql
  - packages/tamthuc_kb/tests/test_curation.py
  - packages/tamthuc_kb/tests/fixtures/review_cases.json
  - docs/contracts/curation-review.schema.json
---

## §1 - Description (BCP-14 normative)

This task is the human curation workflow over knowledge-base content: an expert (master) reviews the interpretation patterns (TASK-KB-002) and the classical excerpts (TASK-KB-003) through a review queue, accepts or rejects each with a required reason, and every accepted change bumps a monotonic version and appends to a retained history. It is the authoring-time human-in-the-loop for the knowledge base, and it encodes the RISK-9 "expert review each release" process as a gate. It does NOT author the patterns (TASK-KB-002) or the corpus (TASK-KB-003); it reviews, versions, and signs off on exactly those rows.

A reviewable object SHALL be either a `pattern` (a TASK-KB-002 row) or a `classical_unit` (a TASK-KB-003 unit). A submission SHALL create a `ReviewItem` in state `in_review` carrying a snapshot of the object version under review; the queue SHALL surface pending items to a reviewer holding the master/expert role (TASK-AUTH-002). A decision SHALL be `accept` or `reject`, SHALL carry a non-empty `reason` in both cases, and SHALL be recorded as an immutable `ReviewDecision` with the reviewer id and timestamp (an audit trail). On `accept` the object's version SHALL increment and the object SHALL become eligible for the active set (a pattern becomes loadable into `knowledge_patterns`; a unit becomes loadable into the corpus); on `reject` the object SHALL stay out of the active set with the reason retained. A reviewer SHALL NOT decide their own submission where the role model distinguishes author and reviewer.

The workflow SHALL expose a release gate: for a named release, every active object whose current version has changed since the last release SHALL have an `accept` decision at that current version, or the gate SHALL fail and name the unsigned objects. This is the mechanism that makes "expert review each release" (strategy RISK-9) a checkable condition rather than an intention. Versioning SHALL be monotonic and non-destructive: a superseded version is retained in history, never overwritten, so a chart or an eval result can be traced to the exact object version it used.

## §2 - Why this design (rationale for humans)

Both source sets are explicit that the ruleset is content an expert authors and reviews, not code that ships on a developer's say-so (Grok-24 curation). Tam Thuc is a heritage subject with live school disagreements; a pattern's polarity or a translation's nuance is a scholarship judgment, and shipping it unreviewed is how "heritage education" quietly turns into unsourced assertion. A review queue with accept/reject-and-reason turns each knowledge change into a signed, auditable act: someone with the standing to judge looked at this điều or this cách cục and said yes, here is why, at this version. That signature is what lets the product claim its interpretations rest on reviewed scholarship, and it is the same discipline as citation-required interpretation, applied one layer earlier at the knowledge itself.

Making the release gate a hard check is the direct operational form of the RISK-9 mitigation. "Expert review each release" is easy to state and easy to skip under deadline; encoding it as a gate that fails on any unsigned active change means a release physically cannot go out with a pattern or a translation that no expert approved at its shipped version. Monotonic, retained versioning is the other half: because an eval result (TASK-RAG-006) and a cast chart both stamp the object versions they used, and those versions are never overwritten, a quality regression can always be traced to the exact reviewed version that produced it. This task is deliberately a sibling to TASK-RAG-004, not a merge with it: TASK-RAG-004 reviews AI-generated interpretations at query time, while this task reviews the human-authored knowledge base at curation time - different objects, different reviewers' focus, same human-in-the-loop principle (strategy 4.4).

## §3 - Contract (models, queue, review, release gate)

### Models (`tamthuc_kb/curation/models.py`)

```python
class ReviewObjectType(str, Enum): pattern = "pattern"; classical_unit = "classical_unit"
class ReviewState(str, Enum):
    in_review = "in_review"; accepted = "accepted"; rejected = "rejected"

class ReviewItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    object_type: ReviewObjectType
    object_id: str              # pattern id or unit_id
    object_version: int         # the version under review
    state: ReviewState
    submitted_by: str
    submitted_at: datetime
    payload: dict               # snapshot of the row under review (the diff base)

class ReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: str
    object_type: ReviewObjectType
    object_id: str
    reviewer_id: str            # must hold the master/expert role (TASK-AUTH-002)
    decision: Literal["accept", "reject"]
    reason: str                 # required for BOTH accept and reject (non-empty)
    decided_at: datetime
    result_version: int | None  # set on accept: the version this object becomes
```

### Queue and review (`tamthuc_kb/curation/queue.py`, `review.py`)

```python
class CurationQueue(Protocol):
    def submit(self, object_type: ReviewObjectType, object_id: str, version: int,
               payload: dict, by: str) -> ReviewItem: ...        # -> in_review
    def pending(self, object_type: ReviewObjectType | None = None) -> list[ReviewItem]: ...
    def get(self, item_id: str) -> ReviewItem | None: ...
    def decide(self, item_id: str, reviewer_id: str,
               decision: Literal["accept", "reject"], reason: str) -> ReviewDecision: ...
    def history(self, object_type: ReviewObjectType, object_id: str) -> list[ReviewDecision]: ...

def decide(...):
    # 1. require reviewer_id holds the master/expert role; reject self-review where authorship differs
    # 2. require a non-empty reason
    # 3. accept: bump object version, mark item accepted, set object eligible for the active set,
    #            append ReviewDecision(result_version=new_version), write an audit row
    #    reject: mark item rejected, keep object OUT of the active set, append ReviewDecision, audit
    # 4. never overwrite a prior version; history is append-only
```

`RelationalCurationQueue` persists to a `review_queue` + `review_decision` pair in the shared Postgres; `InMemoryCurationQueue` backs the tests.

### Release gate (`tamthuc_kb/curation/release_gate.py`)

```python
def release_gate(release_tag: str, active_objects: list[VersionedRef],
                 queue: CurationQueue, since: ReleasePoint) -> GateReport:
    # for every active pattern/unit whose current version changed since `since`,
    # assert there is an accept ReviewDecision at that exact current version.
    # fail the gate and list every unsigned (object_id, version) otherwise.
```

`GateReport` lists `signed`, `unsigned`, and `unchanged` objects; a non-empty `unsigned` fails the gate. The gate is run in CI at release time (TASK-PLAT-004) and is the checkable form of the RISK-9 per-release expert review.

## §4 - Acceptance criteria

1. `submit` places a `pattern` or a `classical_unit` into `in_review` with a version-stamped snapshot; `pending` returns it; `get` returns its payload.
2. `decide` requires the master/expert role and a non-empty reason: a decision by a non-reviewer, or with an empty reason, is rejected for both `accept` and `reject`.
3. `accept` bumps the object version, records a `ReviewDecision` with `result_version`, marks the object eligible for the active set, and appends (never overwrites) history; a second accept bumps again and both versions remain in `history`.
4. `reject` keeps the object out of the active set, records the reason, and leaves the prior active version (if any) untouched.
5. `release_gate` passes when every changed active object has an accept decision at its current version, and fails naming the unsigned `(object_id, version)` when one does not (the RISK-9 gate).
6. Every decision writes an audit row (actor, object, version, decision, reason, timestamp); the audit is queryable via `history`.

## §5 - Verification

- `tests/test_curation.py`: the submit -> pending -> decide lifecycle for both object types; the role guard and the required-reason guard (accept and reject); version bump on accept and append-only history across two accepts; reject keeping the object inactive; the release-gate pass and fail cases against `fixtures/review_cases.json`.
- Audit: assert one immutable audit row per decision and that `history` returns them in order; assert no code path overwrites a prior version.
- Backend parity: run the lifecycle through the `RelationalCurationQueue` (test Postgres or fake) and the `InMemoryCurationQueue`; assert identical `pending` / `history` results.
- Schema: `docs/contracts/curation-review.schema.json` validates `ReviewItem` and `ReviewDecision`; the Pydantic models and the JSON Schema are checked for parity in CI.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_kb`, `pytest packages/tamthuc_kb` (default suite in-memory; the Postgres path behind a marker).

## §6 - Implementation skeleton

1. `curation/models.py`: `ReviewItem`, `ReviewDecision`, the enums; author `docs/contracts/curation-review.schema.json`.
2. `curation/queue.py`: the `CurationQueue` protocol, `RelationalCurationQueue`, `InMemoryCurationQueue`.
3. `migrations/0003_curation.sql`: `review_queue` and `review_decision` tables (append-only decisions), with an actor/object/version audit shape.
4. `curation/review.py`: `decide` with the role guard, required-reason guard, version bump, active-set eligibility, audit write.
5. `curation/release_gate.py`: the per-release signed/unsigned check and `GateReport`.
6. Wire the role check to TASK-AUTH-002 (master/expert), and the active-set effects to TASK-KB-002 (`knowledge_patterns` load) and TASK-KB-003 (corpus load).

## §7 - Dependencies

Depends on TASK-KB-002 (the 150-200 patterns this workflow reviews and versions; TASK-KB-002's own open question defers the sign-off workflow to this task). Reviews TASK-KB-003 classical units through the same queue. Uses TASK-AUTH-002 for the master/expert reviewer role and TASK-PLAT-003 for the `review_queue` / `review_decision` tables and audit rows (soft edge; the physical tables are applied through the PLAT runner). Blocks nothing in the catalog, but gates releases (the RISK-9 per-release expert review) and feeds TASK-RAG-006, which stamps the object versions it evaluated. Sibling to TASK-RAG-004: same human-in-the-loop principle, different object (knowledge content here, AI interpretations there).

## §8 - Example payloads

```json
// a ReviewItem for a pattern awaiting expert sign-off
{ "id": "rev_0007", "object_type": "pattern", "object_id": "qimen_thanh_long_hoi_dau",
  "object_version": 2, "state": "in_review", "submitted_by": "author_ln",
  "submitted_at": "2026-07-08T09:00:00Z",
  "payload": { "id": "qimen_thanh_long_hoi_dau", "polarity": "cat", "version": 2,
    "meaning_modern": "A favorable window for initiating; frame as timing, not a guarantee.",
    "citations": ["yba_dieu_012"] } }
```

```json
// the reviewer's accept decision (reason required, version stamped)
{ "item_id": "rev_0007", "object_type": "pattern", "object_id": "qimen_thanh_long_hoi_dau",
  "reviewer_id": "master_tue", "decision": "accept",
  "reason": "Polarity and citation match Yen Ba Dieu Tau Ca dieu 12; modern gloss avoids a verdict.",
  "decided_at": "2026-07-08T11:20:00Z", "result_version": 2 }
```

## §9 - Open questions

- Whether a school-variant reading is a new version of one object or a separate variant object. Default: a variant that changes only the meaning gloss is a new version with the difference recorded in the reason; a variant that changes polarity is a separate versioned object (coordinate with TASK-KB-002's same open question).
- Author-reviewer separation strength. Default: forbid self-review when authorship is recorded; allow it with a logged override for a solo-expert MVP, surfaced in the audit so it is never silent.
- Whether the release gate blocks the deploy or only warns at MVP. Default: warn-with-named-unsigned in P2, harden to a blocking gate before the public heritage-education launch (align with TASK-LEGAL-004 sign-off).

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Unreviewed content ships | an active pattern/unit changed with no accept at its version | release gate fails, names the unsigned `(object_id, version)`; release blocked/warned per policy |
| Reasonless decision | accept or reject with an empty reason | rejected; a reason is required for both outcomes |
| Unauthorized reviewer | a non-master role decides | rejected; only the master/expert role (TASK-AUTH-002) may decide |
| History overwrite | a new version overwrites a prior one | forbidden; versions are append-only; history retains every superseded version |
| Self-review slips through | author signs off own submission silently | blocked where authorship differs, or logged as an explicit override, never silent |
| Rejected content leaks active | a rejected object still loads | reject keeps the object out of the active set; the loader reads only accepted current versions |

## §11 - Notes

This task turns the knowledge base from a set of committed files into reviewed, versioned, signed scholarship, which is what a heritage-education product must be able to claim. It is marked SHOULD at P2 because the P0/P1 seed can ship with a lighter "cited and curator-checked" bar (TASK-KB-002's default), but the release gate is the piece that makes "expert review each release" (RISK-9) real rather than aspirational, so wire it into CI as soon as it exists. Keep it a clean sibling of TASK-RAG-004 - do not merge the two queues; they review different objects for different reasons even though both express the human-in-the-loop rule. The package `tamthuc_kb` is shared with TASK-KB-001/002/003/005; this task adds the `curation/` module, so the knowledge base stays one installable, mypy-clean unit.
