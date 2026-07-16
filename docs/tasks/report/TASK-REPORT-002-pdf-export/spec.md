---
id: TASK-REPORT-002
title: "PDF export - render the REPORT-001 StructuredReport into a templated, CyberSkill-branded, bilingual PDF; the deterministic chart summary is visually separated from the AI interpretation, and the AIDisclosure and citations are printed; read-only over the report, never re-computes"
module: REPORT
priority: SHOULD
status: done
phase: P1
slice: 1
lang: python
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.1, strategy 7, Claude-07 s5.1, Claude-07 s5.4, Grok-08]
related_frs: [TASK-REPORT-001, TASK-REPORT-003, TASK-RAG-003, TASK-WEB-005, TASK-WEB-006, TASK-LEGAL-001]
depends_on: [TASK-REPORT-001]
blocks: []
new_paths:
  - packages/tamthuc_report/pdf_export.py
  - packages/tamthuc_report/templates/report.html.j2
  - packages/tamthuc_report/templates/report.css
  - packages/tamthuc_report/tests/test_pdf_export.py
---

## §1 - Description (BCP-14 normative)

This task renders the TASK-REPORT-001 `StructuredReport` into a PDF. The module SHALL take a `StructuredReport` and produce a templated, CyberSkill-branded, bilingual (vi / en) PDF. The chart summary and detected patterns (the deterministic half) SHALL be rendered in a section visually separated from the AI interpretation (the AI half) - the engine / AI boundary made visible on the page (strategy 4.1). The AIDisclosure SHALL be printed on the report, and the citations SHALL be printed as a reference list keeping the Han + phien am / bach thoai + dich + locator (the TASK-RAG-003 citation cards).

The module SHALL be read-only over the `StructuredReport`: it renders what REPORT-001 assembled and MUST NOT re-cast, re-interpret, recompute confidence, or alter any field. Branding SHALL follow the CyberSkill Design System v1.3.0 (Umber #45210E, Ochre #F4BA17, Be Vietnam Pro), and glass / elevation SHALL collapse to solid surfaces on print (Claude-07 s5.4). The output SHALL be deterministic given a fixed report (modulo an embedded timestamp).

## §2 - Why this design (rationale for humans)

A report becomes a durable, shareable, printable artifact at PDF (Grok-08); it is the thing a user keeps and forwards, so two properties matter most. First, the engine / AI boundary must stay visible on paper, not just on screen: the deterministic chart summary sits in its own panel and the AI interpretation in another, so a reader always knows which part is oracle-exact calculation and which is cited AI reading (strategy 4.1, Claude-07 s5.3). Printing the AIDisclosure and the full citation list is the same discipline - the label and the sources travel with the document.

Second, the exporter must be a pure renderer. REPORT-001 already validated citation-required and the AIDisclosure and carried confidence unchanged; if the exporter recomputed or tidied anything, a printed report could disagree with the stored one. So it reads the `StructuredReport` and only lays it out. The print-specific rules from the design system (glass collapses to solid, elevation becomes an Ochre border in high contrast) exist because Han and Vietnamese diacritics need contrast to stay legible (Claude-07 s5.1, s5.4); a translucent surface or a too-tight line-height clips a dau nga or a dau nang and corrupts the meaning.

## §3 - Contract (renderer / template)

### Entry point (`pdf_export.py`)

```python
from typing import Literal
from tamthuc_report.models import StructuredReport

def export_pdf(report: StructuredReport, lang: Literal["vi", "en", "bi"] = "bi") -> bytes:
    # render report.html.j2 + report.css with the report:
    #   - chart-summary + detected-patterns panel, visually separated from the interpretation panel
    #   - AIDisclosure block + citation reference list (han + bach_thoai + dich + locator)
    #   - CyberSkill brand (Umber / Ochre, Be Vietnam Pro); solid surfaces on print
    # read-only: never mutates the report, never calls the engine / RAG. returns PDF bytes.
```

### Template structure (`report.html.j2`)

- Header: the CyberSkill brand (Umber band, Ochre mark), `report_id` / `query_id`, `created_at`.
- Panel A (deterministic): `he`, `dau_vao` echo, `lich_phap_summary`, `key_positions`, and the `detected_patterns` table with Han. Labeled and boxed as "Engine - deterministic".
- Panel B (AI): the beginner interpretation, the expert interpretation, and the recommendations. Labeled "AI interpretation".
- AIDisclosure block: `model`, `limits`, `review_status`, printed from the report.
- Citations: a reference list, each with `source`, `locator`, `han`, `bach_thoai`, `dich`.
- Bilingual: vi and en, sectioned per lang (the TASK-WEB-006 content split).

### Print rules (`report.css`)

Brand tokens (Umber / Ochre, Be Vietnam Pro); solid surfaces on print (no glass); elevation becomes a high-contrast border; a diacritic-safe line-height so Vietnamese dau chong and Han are not clipped (Claude-07 s5.1). Panels A and B are distinct, labeled blocks.

## §4 - Acceptance criteria

1. `export_pdf(report)` returns PDF bytes rendering the `StructuredReport` with a chart-summary / patterns panel and an interpretation panel that are visually separated (distinct, labeled sections).
2. The AIDisclosure (`model`, `limits`, `review_status`) is printed on the report.
3. The citations are printed as a reference list keeping `han` + `bach_thoai` + `dich` + `locator` for each.
4. Branding follows the design system (Umber / Ochre, Be Vietnam Pro); surfaces are solid on print (no glass), diacritics and Han are not clipped.
5. Bilingual output renders vi and en; the `lang` argument selects vi, en, or bilingual.
6. `export_pdf` is read-only: it never mutates the report and never calls the engine / RAG (a spy + a before/after equality check).

## §5 - Verification

- `test_pdf_export.py`: render a golden `StructuredReport` (from the TASK-REPORT-001 fixtures) -> PDF; extract the text; assert the chart-summary section, the interpretation section, the AIDisclosure, and every citation (han + dich + locator) are present, and that the two panels are distinct sections.
- Separation test: assert the deterministic panel and the AI panel are separate blocks (distinct section markers / headings), not interleaved.
- Read-only: deep-copy the report, export, assert it is byte-identical after and that no engine / RAG client was called (a spy).
- Branding / print: assert the CSS applies solid surfaces on print and the brand colors / fonts; a dau chong (diacritic-clip) check on a Vietnamese + Han sample line.
- Determinism: two exports of the same report are identical modulo the embedded timestamp.
- Gates: `python -m pytest packages/tamthuc_report`, `ruff check`, `mypy packages/tamthuc_report`.

## §6 - Implementation skeleton

1. `report.html.j2`: header, Panel A (deterministic), Panel B (AI), the AIDisclosure block, the citation list; bilingual.
2. `report.css`: the brand tokens + print rules (solid surfaces, high-contrast borders, diacritic-safe line-height).
3. `pdf_export.py`: `export_pdf(report, lang)` rendering HTML + CSS to PDF (a headless renderer), read-only.
4. `tests/test_pdf_export.py`: golden report -> PDF text extraction; separation, read-only, branding, determinism.

## §7 - Dependencies

Depends on TASK-REPORT-001 (the `StructuredReport` it renders; reuses its models and the RAG-003 citation cards / AIDisclosure). Follows the TASK-WEB-006 vi / en content split for bilingual output and the TASK-LEGAL-001 AI-disclosure copy. Renders the same object TASK-WEB-005 shows on screen. Consumes the CyberSkill Design System v1.3.0 tokens (Claude-07 s5). Nothing depends on it (blocks empty).

## §8 - Example payloads

```
# Rendered PDF layout (schematic) - two separated panels + disclosure + citations
[ Umber header | Ochre mark | report_id | created_at ]

+-- Panel A - Engine (deterministic) ------------------+
| he: ky_mon   Tu tru 癸未 甲子 戊午 丁巳   tiet khi 冬至 |
| detected_patterns: 青龍返首 (cat, cung 1, score 0.9)  |
+------------------------------------------------------+

+-- Panel B - AI interpretation -----------------------+
| beginner: ... (cited)   expert: ... (cited)          |
| recommendations: ...                                 |
+------------------------------------------------------+

AIDisclosure: model=... | decision support, not a verdict | review: pending
Citations: [1] Yen Ba Dieu Tau Ca - cach cat - 青龍返首 - bach thoai ... - dich ...
```

## §9 - Open questions

- Bilingual layout: side-by-side columns vs vi-then-en sections. Default: sectioned per lang for readability with Han; side-by-side is a later refinement.
- Renderer choice (WeasyPrint vs headless Chromium). Default: an HTML + CSS-to-PDF renderer that honors the design-system CSS and embeds Be Vietnam Pro; decide in implementation and keep the template renderer-agnostic.
- Whether the 9-palace chart image is embedded (from the TASK-CHART-004 export) or the PDF is text + table only. Default: text + the cach cuc table at MVP; embed the chart image when the CHART-004 export is available.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Boundary invisible | chart summary and interpretation interleaved | forbidden; two visually separated, labeled panels (strategy 4.1) |
| Missing AIDisclosure / citations | the printed report drops the label or the sources | required on every export; a test asserts presence |
| Re-compute at export | the exporter re-interprets or recomputes confidence | forbidden; read-only renderer; spy + equality test |
| Clipped diacritics / Han | line-height too tight on print | dau chong check; diacritic-safe CSS (Claude-07 s5.1) |
| Glass on print | a translucent surface reduces contrast | collapses to solid on print (Claude-07 s5.4) |
| Non-deterministic output | render varies run to run | deterministic modulo the embedded timestamp |

## §11 - Notes

Package `tamthuc_report` (Python, DEC-2). PDF export is the report made durable and shareable (Grok-08). Two things carry over from REPORT-001's discipline: the engine / AI boundary stays visible (a deterministic panel separated from the AI interpretation panel), and the AIDisclosure and full citation list are printed so the label and the sources travel with the document (strategy 4.1, 7). It is a pure renderer - read-only over the `StructuredReport`, never re-computing - and it follows the CyberSkill Design System v1.3.0 with print rules that keep Han and Vietnamese diacritics legible (Claude-07 s5.1, s5.4). TASK-REPORT-003 supplies the per-question-type template this export renders.
