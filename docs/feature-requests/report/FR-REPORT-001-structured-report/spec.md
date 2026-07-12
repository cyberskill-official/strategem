---
id: FR-REPORT-001
title: "Structured report assembly - compose {chart summary, detected patterns, beginner/expert interpretation, recommendations, citations, confidence, AIDisclosure} from the la so envelope + RAG-003 output; persist per PLAT-003; read-only over the chart"
module: REPORT
priority: MUST
status: done
phase: P1
slice: 1
lang: python
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.2, strategy 4.3, strategy 5, Grok-33, Grok-08]
related_frs: [FR-REPORT-002, FR-REPORT-003, FR-RAG-003, FR-PLAT-002, FR-PLAT-003, FR-API-004]
depends_on: [FR-RAG-003]
blocks: [FR-REPORT-002, FR-WEB-005]
new_paths:
  - packages/tamthuc_report/__init__.py
  - packages/tamthuc_report/models.py
  - packages/tamthuc_report/assemble.py
  - packages/tamthuc_report/repo.py
  - packages/tamthuc_report/tests/test_assemble.py
  - packages/tamthuc_report/tests/fixtures/report_golden.json
---

## §1 - Description (BCP-14 normative)

This FR assembles the two branches of the platform into one durable artifact: it takes the la so envelope the deterministic engine cast (FR-PLAT-002) and the structured interpretation the RAG branch produced (FR-RAG-003) and composes a single `StructuredReport` object, then persists it. It is step 7 of the nine-step query flow (strategy 4.2).

The module SHALL produce a `StructuredReport` containing: a chart summary (he, echoed input, a human-readable calendar line, the salient positions), the detected patterns (from the envelope `cach_cuc`), a beginner interpretation and an expert interpretation, a recommendations list, the citations, a confidence value, and an AIDisclosure. The chart summary and detected patterns SHALL be copied from the envelope; the interpretation, recommendations, citations, confidence, and AIDisclosure SHALL be taken from the RAG-003 output. The module MUST NOT re-cast a chart, re-run retrieval, re-prompt the LLM, or recompute confidence - it is an assembler and a persister, and it is read-only over the chart fields (`ban`, `cach_cuc`, `lich_phap`, `co_truong_phai`) exactly as the RAG branch is (strategy 4.3).

Every claim in the interpretation SHALL carry at least one citation and every report SHALL carry a non-empty AIDisclosure; the module SHALL reject at assembly time (before persistence) any report that violates either, rather than persist an unsound artifact. The module SHALL persist one row in the FR-PLAT-003 `reports` table keyed by `report_id` and `query_id`, with an audit row (strategy 4.2 step 9).

## §2 - Why this design (rationale for humans)

The whole platform rests on the split between a deterministic engine and an AI layer bound by the la so JSON (strategy 4.1). The report is where the two halves finally meet and become one thing a user reads and keeps - so the report is exactly where the boundary is most tempting to cross. If the assembler "tidies up" a chart position or recomputes a score to make the prose match, determinism and reproducibility are gone. Making REPORT a strict copy-from-envelope plus copy-from-RAG assembler, with no path to write a chart field, keeps the boundary intact at the last mile.

Enforcing citation-required and AIDisclosure at assembly, not just at RAG output, is defense in depth. RAG-003 already gates these; REPORT gates them again because REPORT is the last stop before persistence and the user, and a report is a durable, shareable, potentially exported artifact (PDF at REPORT-002). An uncited claim that reaches a saved, printed report is worse than one caught in a transient API response. The beginner/expert/recommendations shape comes straight from the Grok report design (Grok-33, Grok-08): one artifact serves both a casual reader and a practitioner.

## §3 - Contract (schema / types)

### Pydantic models (`packages/tamthuc_report/models.py`)

```python
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class Citation(BaseModel):            # shape shared with FR-RAG-003
    model_config = ConfigDict(extra="forbid")
    source: str                       # e.g. "Tat phap phu"
    locator: str                      # chapter / law number
    han: str | None = None
    bach_thoai: str | None = None
    dich: str | None = None

class ChartSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    he: str                           # luc_nham | ky_mon | thai_at  (copied)
    dau_vao: dict                     # echoed from the envelope (copied)
    lich_phap_summary: str            # human-readable line: tu tru + tiet khi (rendered from copied fields)
    key_positions: list[str]          # salient positions the engine provided (copied)

class ReportPattern(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str; name: str
    polarity: str                     # cat | hung | trung  (copied from cach_cuc)
    cung: int | None = None
    score: float | None = None
    citations: list[Citation]

class Interpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    beginner: str                     # from RAG-003
    expert: str                       # from RAG-003
    recommendations: list[str]        # from RAG-003

class AIDisclosure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str
    limits: str
    review_status: str                # pending | approved | not_required

class StructuredReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_id: UUID
    query_id: UUID
    chart_summary: ChartSummary       # copied from the envelope
    detected_patterns: list[ReportPattern]   # copied from cach_cuc
    interpretation: Interpretation    # from RAG-003
    citations: list[Citation]         # from RAG-003
    confidence: float                 # carried from RAG-003, never recomputed
    ai_disclosure: AIDisclosure       # mandatory, non-empty
    created_at: datetime
```

### The assembler (`assemble.py`)

```python
def assemble(envelope: LaSo, interp: RagOutput, query_id: UUID) -> StructuredReport:
    # chart_summary + detected_patterns: COPY from envelope (he, dau_vao, lich_phap, cach_cuc)
    # interpretation + citations + confidence + ai_disclosure: COPY from interp (RAG-003)
    # validate: every interpretation claim cited; ai_disclosure non-empty
    # returns the object; pure, no I/O
```

`assemble` is pure and does no I/O. Persistence is `repo.persist(report)`, which writes the FR-PLAT-003 `reports` row and the audit row. The read-only rule is a hard invariant: `assemble` reads the envelope's chart fields and never returns an object whose chart fields differ from the source.

## §4 - Acceptance criteria

1. Given a golden envelope + a golden RAG-003 output, `assemble` returns a `StructuredReport` whose `chart_summary.he`, `chart_summary.dau_vao`, and `detected_patterns` are equal to the envelope's `he`, `dau_vao`, and `cach_cuc` (copy-equality), and whose `interpretation`, `citations`, and `confidence` equal the RAG output's (provenance-equality).
2. A report whose interpretation contains a claim with no citation is rejected at assembly (raises), never persisted.
3. `ai_disclosure` is always present and non-empty; a missing or empty disclosure is rejected.
4. `confidence` equals the RAG-003 confidence exactly; the assembler never recomputes it.
5. `persist` writes exactly one `reports` row (keyed by `report_id` + `query_id`) and one audit row; a load-back round-trips the object.
6. `assemble` performs no engine call and no retrieval call, and never mutates a chart field (asserted by a read-only test that diffs the envelope before and after).

## §5 - Verification

- pytest: golden envelope + golden RAG output -> golden `StructuredReport` (`fixtures/report_golden.json`); copy-equality on chart fields; provenance-equality on interpretation fields.
- Validation tests: an uncited-claim fixture is rejected; a missing-AIDisclosure fixture is rejected.
- Persistence test against a FR-PLAT-003 test database (or a fake repo): `assemble` then `persist` then load round-trips; the audit row exists.
- Read-only test: deep-copy the envelope, run `assemble`, assert the envelope is byte-identical afterward and that no engine/retrieval client was invoked (a spy).
- Gates: `python -m pytest packages/tamthuc_report`, `ruff check`, `mypy packages/tamthuc_report`.

## §6 - Implementation skeleton

1. Create the `tamthuc_report` package (`models.py`, `assemble.py`, `repo.py`, `tests/`).
2. `models.py`: the models above; import `Citation` and `AIDisclosure` from the FR-RAG-003 schema so the two never drift (single shape).
3. `assemble.py`: `assemble(envelope, interp, query_id)` - copy chart fields, copy interpretation fields, validate citation-required + AIDisclosure, build the object; pure.
4. `repo.py`: `persist(report)` - write the `reports` row + audit row per FR-PLAT-003; `load(report_id)`.
5. Wire into the API at step 7 (strategy 4.2); the API passes the cast envelope and the RAG output.
6. Golden fixtures + the validation, persistence, and read-only tests.

## §7 - Dependencies

Depends on FR-RAG-003 (its structured output is the interpretation, recommendations, citations, confidence, and AIDisclosure source, and its `Citation` / `AIDisclosure` shapes are reused). Reads the FR-PLAT-002 la so envelope for the chart summary and detected patterns. Persists per FR-PLAT-003 (the `reports` and audit tables; FR-API-004 owns query/chart persistence, REPORT owns the report row). Blocks FR-REPORT-002 (PDF export renders this object) and FR-WEB-005 (the report-view screen).

## §8 - Example payloads

A `StructuredReport` for a QiMen chart (abridged):

```json
{
  "report_id": "b1c2...",
  "query_id": "a0f1...",
  "chart_summary": {
    "he": "ky_mon",
    "dau_vao": { "datetime": "2004-01-01T10:30:00", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "trach_thoi" },
    "lich_phap_summary": "Tu tru 癸未 甲子 戊午 丁巳 - tiet khi 冬至 (tam nguyen thuong)",
    "key_positions": ["truc phu cung 1", "truc su Khai mon cung 6"]
  },
  "detected_patterns": [
    { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "polarity": "cat", "cung": 1, "score": 0.9,
      "citations": [ { "source": "Yen Ba Dieu Tau Ca", "locator": "cach cat" } ] }
  ],
  "interpretation": {
    "beginner": "... (cited)",
    "expert": "... (cited)",
    "recommendations": ["..."]
  },
  "citations": [ { "source": "Yen Ba Dieu Tau Ca", "locator": "cach cat", "han": "青龍返首" } ],
  "confidence": 0.72,
  "ai_disclosure": { "model": "...", "limits": "decision support, not a verdict; no medical/legal/financial advice",
                     "review_status": "pending" },
  "created_at": "2026-07-08T12:00:05Z"
}
```

## §9 - Open questions

- Does REPORT store the full envelope or reference the chart by `query_id`? Default: store the report and reference the chart (charts are persisted by FR-API-004), to avoid duplicating the chart. If audit needs an immutable snapshot, store the envelope hash alongside and revisit.
- beginner / expert split: does REPORT choose a persona or echo both? Default: RAG-003 emits both (Grok-33); REPORT echoes and never re-prompts. The reader picks the layer in the UI.
- Confidence display: REPORT carries the number; how WEB-005 renders it (band vs raw) is a UI decision, not REPORT's.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| REPORT recomputes a chart fact | assembler re-derives a position or score | forbidden; copy-only from the envelope; the read-only / mutation test fails |
| Uncited claim in a report | RAG output had an uncited span | assembly-time validation rejects; do not persist |
| Missing AIDisclosure | assembler omitted it | schema requires it; validation fails before persistence |
| Report persisted without an audit row | repo path skipped the audit write | persistence test asserts the audit row exists |
| Confidence altered | assembler overwrote the RAG confidence | provenance test asserts `confidence == interp.confidence` |

## §11 - Notes

Package `tamthuc_report` (Python, DEC-2). It assembles chart + patterns + interpretation into a structured report with beginner, expert, and recommendation layers (Grok-33, Grok-08), then hands the object to FR-REPORT-002 for PDF. It reads the engine and RAG output and never re-computes - the same read-only boundary the RAG branch obeys (strategy 4.3). This is the P1 join point where the deterministic chart and the cited interpretation become one persisted, auditable artifact for FR-WEB-005 and the PDF export. Confidence is carried from RAG-003 unchanged; the assembler owns composition and validation, not judgment.
