---
id: TASK-REPORT-003
title: "Sample report templates per question type - trach thoi (timing), phuong vi (direction), chu-khach (competitor/risk), and macro outlook - each mapped to the right system and dung than per Claude-07 s1; presentation templates over the REPORT-001 report, read-only, no re-compute"
module: REPORT
priority: COULD
status: done
phase: P2
slice: 1
lang: python
effort_h: 6
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s1.1, Claude-07 s1.2, Claude-07 s1.3, Claude-07 s1.4, Grok-08]
related_frs: [TASK-REPORT-001, TASK-REPORT-002, TASK-QMDG-007, TASK-STRAT-003, TASK-WEB-005]
depends_on: [TASK-REPORT-001]
blocks: []
new_paths:
  - packages/tamthuc_report/templates.py
  - packages/tamthuc_report/templates/question_types/trach_thoi.md
  - packages/tamthuc_report/templates/question_types/phuong_vi.md
  - packages/tamthuc_report/templates/question_types/chu_khach.md
  - packages/tamthuc_report/templates/question_types/vi_mo.md
  - packages/tamthuc_report/tests/test_templates.py
---

## §1 - Description (BCP-14 normative)

This task provides sample report templates per question type: trach thoi 擇時 (timing), phuong vi 方位 (direction), chu-khach 主客 (competitor / risk), and vi mo (macro outlook). Each template SHALL shape how a TASK-REPORT-001 `StructuredReport` is presented - the section order, which dung than 用神 to foreground, and the emphasis - and SHALL document the mapping from question type to the right system and dung than per Claude-07 s1: trach thoi -> Ky Mon (Luc Nham for a specific act); phuong vi -> Ky Mon (cuu cung, eight directions); chu-khach -> Thai At / Ky Mon / Luc Nham (host-guest); vi mo -> Thai At (macro, long-range).

The templates SHALL be presentation over the assembled report: read-only, with no re-casting, no re-interpretation, and no field mutation (strategy 4.3). Each template SHALL ship with a sample filled report (Grok-08) demonstrating the shape. A loader SHALL map a report's `loai_cau_hoi` to its template, with a typed default fallback for an unknown type.

## §2 - Why this design (rationale for humans)

A timing question and a macro-outlook question want different reports even though both come through the same assembler (Grok-08). A trach thoi report leads with the recommended window and the cat / hung reasons; a chu-khach report leads with the two-sided posture; a macro report leads with the long-range trend. Hard-coding one layout would serve none of them well.

Templating the presentation per question type - while keeping REPORT-001 as the single assembler - gives each question the report shape that fits it without duplicating assembly logic. The templates also encode the Claude-07 s1 mapping (which system and which dung than each question type calls for) as a documented, shipped artifact, so the reason a timing report uses Ky Mon and foregrounds the acting palace is written down, not folklore. Templates stay read-only over the report for the same reason everything downstream of the envelope is: the deterministic / AI boundary must not be crossed at presentation (strategy 4.3), and a template must never quietly re-cast to a system it thinks is "better" than the one actually cast.

## §3 - Contract (mapping and loader)

### Mapping (Claude-07 s1)

| Question type | System (he) | dung than focus | Report leads with |
|---|---|---|---|
| trach thoi 擇時 (timing) | Ky Mon (Luc Nham for a specific act) | the matter + the chosen hour | the recommended window + cat / hung |
| phuong vi 方位 (direction) | Ky Mon (cuu cung, 8 huong) | the direction palace | the favorable / unfavorable directions |
| chu-khach 主客 (competitor / risk) | Thai At / Ky Mon / Luc Nham | self (chu) + other (khach) | the two-sided posture |
| vi mo (macro outlook) | Thai At | the trend / cycle | the long-range trend |

### Loader (`templates.py`)

```python
from pydantic import BaseModel, ConfigDict
from tamthuc_report.models import StructuredReport

class ReportTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_type: str                # trach_thoi | phuong_vi | chu_khach | vi_mo
    he: list[str]                     # recommended system(s) per Claude-07 s1
    dung_than_focus: str
    section_order: list[str]          # how to order the StructuredReport sections
    sample_path: str                  # the shipped sample report

def template_for(loai_cau_hoi: str) -> ReportTemplate: ...   # question type -> template, typed default fallback

def render_sections(report: StructuredReport, template: ReportTemplate) -> list["Section"]:
    # reorder / label the report's existing sections per the template; read-only, no re-compute
    ...
```

Each question-type markdown ships the mapping plus a sample filled report (Grok-08). `render_sections` only reorders and labels the report's own content; it adds nothing and derives nothing.

## §4 - Acceptance criteria

1. Four templates exist - `trach_thoi`, `phuong_vi`, `chu_khach`, `vi_mo` - each documenting its system(s), dung than focus, and section order per Claude-07 s1.
2. `template_for` maps a report's `loai_cau_hoi` to the right template; an unknown type returns a typed default (not a crash).
3. `render_sections` reorders / emphasizes the `StructuredReport`'s existing sections and never adds, recomputes, or mutates content (read-only).
4. Each template ships a sample filled report (Grok-08) matching its shape.
5. The mapping matches Claude-07 s1 (timing -> Ky Mon, direction -> Ky Mon cuu cung, chu-khach -> Thai At / Ky Mon / Luc Nham, macro -> Thai At).
6. The templates feed TASK-REPORT-002 (PDF) and TASK-WEB-005 (report view) without changing the assembled report.

## §5 - Verification

- `test_templates.py`: `template_for` returns the right template per question type; an unknown type returns the default; `render_sections` over a golden `StructuredReport` reorders sections without changing their content (set-equality of content before and after, order differs).
- Read-only: the `StructuredReport` is byte-identical after `render_sections` (only an ordered list of sections / labels is produced).
- Mapping: assert each template's `he` and `dung_than_focus` match the Claude-07 s1 table.
- Samples: each shipped sample report validates against the TASK-REPORT-001 schema.
- Gates: `python -m pytest packages/tamthuc_report`, `ruff check`, `mypy packages/tamthuc_report`.

## §6 - Implementation skeleton

1. `templates.py`: `ReportTemplate`, `template_for`, `render_sections` (read-only reorder / label).
2. `question_types/{trach_thoi,phuong_vi,chu_khach,vi_mo}.md`: the mapping + a sample filled report each (Grok-08).
3. The typed default-fallback template for an unknown type.
4. `tests/test_templates.py`: the mapping, `template_for`, the read-only render, and sample-schema validation.

## §7 - Dependencies

Depends on TASK-REPORT-001 (the `StructuredReport` whose sections it reorders; read-only). Aligns with TASK-QMDG-007 (dung than by question type - the same mapping the templates encode) and TASK-STRAT-003 (the chu-khach template mirrors the chu-khach decision frame). Consumed by TASK-REPORT-002 (PDF) and TASK-WEB-005 (report view). Nothing depends on it (blocks empty).

## §8 - Example payloads

```json
// ReportTemplate for a timing question
{ "question_type": "trach_thoi",
  "he": ["ky_mon", "luc_nham"],
  "dung_than_focus": "the matter + the chosen hour",
  "section_order": ["recommended_window", "detected_patterns", "beginner", "expert",
                    "recommendations", "ai_disclosure", "citations"],
  "sample_path": "templates/question_types/trach_thoi.md" }
```

## §9 - Open questions

- Does the template pick the system, or only reflect what was cast? Default: the template documents the recommended system per Claude-07 s1 and reflects the system actually cast; it never re-casts to a "preferred" system.
- Overlap with TASK-QMDG-007 (the dung than mapping). Default: QMDG-007 owns the engine-side dung than palace; REPORT-003 owns the presentation mapping; both cite the same Claude-07 s1 source.
- More question types later (e.g. hon nhan, tai loc). Default: the four canonical types at MVP; add templates as question types are formalized.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Template re-computes | render adds / derives content | forbidden; read-only reorder / label only; byte-equality test |
| Wrong system mapping | a timing template points at Thai At | mapping fixed to Claude-07 s1; a test asserts |
| Unknown question type crashes | no template for a type | a typed default fallback, not a crash |
| Sample drifts from schema | a shipped sample is invalid | the sample validates against the TASK-REPORT-001 schema in CI |
| Layout hides the AI boundary | a template interleaves engine + AI content | the section order keeps the deterministic and AI sections distinct (TASK-REPORT-002 renders them separated) |

## §11 - Notes

Package `tamthuc_report` (Python, DEC-2). Report templates give each question type the report shape that fits it - trach thoi leads with the window, chu-khach with the two-sided posture, macro with the long-range trend - while keeping REPORT-001 as the single assembler and staying read-only over the assembled report (Grok-08, strategy 4.3). Each template also encodes the Claude-07 s1 mapping from question type to system and dung than as a shipped, documented artifact (timing -> Ky Mon, direction -> Ky Mon cuu cung, competitor / risk -> Thai At / Ky Mon / Luc Nham, macro -> Thai At), so the presentation reasons are written down. Feeds the PDF export (TASK-REPORT-002) and the report-view screen (TASK-WEB-005).
