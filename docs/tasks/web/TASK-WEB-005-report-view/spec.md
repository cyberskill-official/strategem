---
id: TASK-WEB-005
title: "Report view screen - renders the REPORT-001 StructuredReport (chart summary / detected patterns / beginner+expert interpretation / recommendations / citations) with the deterministic chart summary visually separated from the AI interpretation, a mandatory AIDisclosureBadge, and a PDF download (REPORT-002)"
module: WEB
priority: SHOULD
status: done
phase: P1
slice: 1
lang: typescript
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s6, strategy 4.4, Grok-33]
related_frs: [TASK-WEB-003, TASK-REPORT-001, TASK-REPORT-002, TASK-WEB-001, TASK-RAG-003, TASK-RAG-004, TASK-CHART-001, TASK-LEGAL-001]
depends_on: [TASK-WEB-003, TASK-REPORT-001]
blocks: []
new_paths:
  - apps/web/src/app/report/[reportId]/page.tsx
  - apps/web/src/components/report/report-view.tsx
  - apps/web/src/components/report/chart-summary-section.tsx
  - apps/web/src/components/report/interpretation-section.tsx
  - apps/web/src/components/report/recommendations-list.tsx
  - apps/web/src/components/report/citation-list.tsx
  - apps/web/src/components/report/pdf-download-button.tsx
  - apps/web/src/lib/api/report.ts
  - apps/web/tests/report-view.test.tsx
---

## §1 - Description (BCP-14 normative)

This task builds the report view screen - the read surface for the durable, persisted report the REPORT module assembled (TASK-REPORT-001). Where the results screen (TASK-WEB-003) is the live outcome of a cast, the report view renders the saved `StructuredReport` artifact: the chart summary and detected patterns (copied from the engine), the beginner and expert interpretation, the recommendations, the citations, the confidence, and the AIDisclosure. It owns the report presentation and the PDF download trigger; it does NOT assemble the report (TASK-REPORT-001) or render it to PDF (TASK-REPORT-002) - it renders the object and asks the backend for the file.

The screen SHALL render, from the TASK-REPORT-001 `StructuredReport` fetched by `report_id`: (a) a deterministic region - the `chart_summary` (`he`, echoed `dau_vao`, the human-readable `lich_phap_summary`, the `key_positions`) and the `detected_patterns` list, each pattern's `polarity` (cat/hung/trung) shown with color AND icon AND text, never color alone (TASK-WEB-001); and (b) an interpreted region - the `interpretation` (beginner and expert, toggleable), the `recommendations`, and the `citations`. The two regions SHALL be visually separated so a reader can always tell the engine's computed summary from the AI's interpretation (strategy 4.4). It MAY embed the full interactive chart (TASK-CHART-001/002/003) by the report's `query_id`; when it does, the chart is read-only.

The screen SHALL display an `AIDisclosureBadge` (TASK-WEB-001) on the interpretation, always, fed by `ai_disclosure` - it is mandatory on any AI output. Where `ai_disclosure.review_status` is `pending`, the screen SHALL mark the report not-yet-approved (and MAY show a `HumanReviewGate`, TASK-RAG-004), distinct from an approved report. The screen SHALL offer a PDF download that calls the TASK-REPORT-002 export for this `report_id` and SHALL show `confidence` as supporting context, not as a headline verdict. It SHALL treat the report object and any embedded envelope as read-only.

## §2 - Why this design (rationale for humans)

The report is the artifact a user keeps, shares, and prints, so it is exactly where the deterministic-and-AI boundary must be most legible (strategy 4.4). REPORT-001 already assembled the two halves under a hard read-only rule; the report view is the last visible mile of that same rule, so it lays the engine's chart summary and detected patterns in one region and the AI's cited interpretation in another, physically separated. Collapsing them into one block would let a saved, exported document read an AI sentence as if it carried the engine's determinism - the one thing the whole architecture exists to prevent, and worse in a durable PDF than in a transient screen.

The AIDisclosureBadge is mandatory and the citations are first-class here for the same reason REPORT enforces them at assembly: a report is durable and shareable, so an uncited claim or a missing disclosure that reaches it is worse than one caught upstream (TASK-REPORT-001 s2). Rendering confidence as supporting context rather than a headline number avoids implying a false precision the tool does not claim - the badge carries the limits copy (TASK-LEGAL-001), and the framing stays decision support, not prophecy (strategy 7). Marking a pending report as not-yet-approved keeps the review state honest into the saved artifact, so a reader never mistakes an unvetted reading for a vetted one.

## §3 - Contract (screen / regions / data)

### Layout (Claude-07 s6, on the TASK-WEB-001 shell)

```
+------------------------- report view -------------------------+
| [ deterministic region - from the engine ]                   |
|   chart summary: he / dau_vao / lich_phap_summary / positions|
|   detected patterns: name / cung / cat|hung (icon + text)    |
|   (optional) embedded chart  (TASK-CHART-001/002/003, read-only)|
| ------------- boundary (visually separated) ---------------- |
| [ interpreted region - AI, labeled ]                         |
|   AIDisclosureBadge  +  persona toggle (beginner | expert)   |
|   interpretation text ... [citation refs]                    |
|   recommendations ...                                        |
|   citations (source / locator / Han / bach thoai / dich)     |
|   confidence (supporting context)                            |
| [ PDF download ]  (TASK-REPORT-002)                            |
+--------------------------------------------------------------+
```

### Data (`lib/api/report.ts`, reads TASK-REPORT-001)

```ts
// mirrors the TASK-REPORT-001 StructuredReport
type StructuredReport = {
  report_id: string; query_id: string;
  chart_summary: { he: string; dau_vao: Record<string, unknown>; lich_phap_summary: string; key_positions: string[] };
  detected_patterns: { id: string; name: string; polarity: "cat" | "hung" | "trung"; cung: number | null; score: number | null; citations: Citation[] }[];
  interpretation: { beginner: string; expert: string; recommendations: string[] };
  citations: Citation[];
  confidence: number;
  ai_disclosure: { model: string; limits: string; review_status: "pending" | "approved" | "not_required" };
  created_at: string;
};
type Citation = { source: string; locator: string; han?: string; bach_thoai?: string; dich?: string };

async function getReport(reportId: string): Promise<StructuredReport>;   // read-only
async function downloadReportPdf(reportId: string): Promise<Blob>;        // TASK-REPORT-002
```

### Regions and controls

- Deterministic region: `chart-summary-section` renders `chart_summary` and the `detected_patterns` with the cat/hung icon+text badge (semantic tokens, never color alone). Optionally embeds the interactive chart by `query_id`.
- Interpreted region: `interpretation-section` renders the persona-selected reading (beginner/expert toggle - both present in the object, no re-fetch), the `recommendations-list`, and the `citation-list` (source / locator / Han / bach thoai / dich). The `AIDisclosureBadge` is always present and reflects `ai_disclosure.review_status`.
- `pdf-download-button` calls `downloadReportPdf(report_id)` (TASK-REPORT-002); the export is the backend's, not a client re-render.

## §4 - Acceptance criteria

1. Given a `StructuredReport` fetched by `report_id`, the screen renders the deterministic region (chart summary + detected patterns) and the interpreted region (beginner/expert + recommendations + citations), visually separated.
2. `AIDisclosureBadge` is present on the interpretation on every report; a report rendered without it fails a test (mandatory, strategy 4.4).
3. Each pattern's cat/hung/trung polarity is shown with color AND icon AND text, never color alone (TASK-WEB-001).
4. The persona toggle switches beginner/expert without a re-fetch (both are in the object); citations render source / locator and the three text layers (Han / bach thoai / dich) where present; in-text refs resolve to their citation.
5. When `ai_disclosure.review_status` is `pending`, the report is marked not-yet-approved, distinct from an approved report.
6. The PDF download calls the TASK-REPORT-002 export for the `report_id` and returns the file; the client does not re-render the PDF itself.
7. `confidence` is shown as supporting context, not a headline verdict; the report object and any embedded envelope are unchanged by the screen (read-only).

## §5 - Verification

- `tests/report-view.test.tsx`: renders a `StructuredReport` fixture (with `review_status` `not_required` and `pending`); asserts the two regions and their visual separation, the always-present `AIDisclosureBadge`, the cat/hung icon+text badges, the persona toggle without re-fetch, the citation three layers + locator, the pending not-yet-approved marking, the PDF-download call to TASK-REPORT-002, and the read-only invariant (object byte-identical after render).
- Accessibility: `jest-axe` clean; the stacked-diacritics clip test (TASK-WEB-001) over the interpretation text, pattern names, and `lich_phap_summary` on light+dark; keyboard-operable persona toggle and download.
- Contract: the `StructuredReport` / `Citation` types are checked against the TASK-REPORT-001 shapes (shared fixture); a drift fails the test.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/api/report.ts`: `getReport(reportId)` and `downloadReportPdf(reportId)` (TASK-REPORT-002) with the auth token; read-only.
2. `chart-summary-section.tsx`: the deterministic region - `chart_summary` + `detected_patterns` with cat/hung icon+text badges; optional embedded chart by `query_id`.
3. `interpretation-section.tsx` (+ persona toggle) + `recommendations-list.tsx` + `citation-list.tsx`: the interpreted region with the mandatory `AIDisclosureBadge` and the pending/approved marking.
4. `pdf-download-button.tsx`: trigger the TASK-REPORT-002 export by `report_id`.
5. `report-view.tsx` + `app/report/[reportId]/page.tsx`: compose the regions and the visual boundary in the TASK-WEB-001 shell; wire the disclaimer slot (TASK-LEGAL-001).
6. `tests/report-view.test.tsx` + the shared TASK-REPORT-001 contract fixture.

## §7 - Dependencies

Depends on TASK-WEB-003 (it builds on the results-screen presentation - the deterministic/AI separation, the mandatory badge, the cat/hung convention, the citation cards) and TASK-REPORT-001 (the `StructuredReport` object it renders). Uses TASK-REPORT-002 for the PDF download, TASK-WEB-001 (`AIDisclosureBadge`, tokens, the icon+text convention), TASK-RAG-003 (the `Citation` / `AIDisclosure` shapes carried into the report), TASK-RAG-004 behind the review marking, TASK-CHART-001/002/003 when embedding the interactive chart, and TASK-LEGAL-001 for the limits copy and disclaimer. It renders the report and any embedded envelope read-only (strategy 4.3).

## §8 - Example payloads

```json
// StructuredReport (abridged) this screen renders (TASK-REPORT-001)
{ "report_id": "b1c2", "query_id": "a0f1",
  "chart_summary": { "he": "ky_mon",
    "dau_vao": { "datetime": "2004-01-01T10:30:00", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "trach_thoi" },
    "lich_phap_summary": "Tu tru 癸未 甲子 戊午 丁巳 - tiet khi 冬至 (tam nguyen thuong)",
    "key_positions": ["truc phu cung 1", "truc su 休門 cung 6"] },
  "detected_patterns": [
    { "id": "qimen_thanh_long_hoi_dau", "name": "青龍返首", "polarity": "cat", "cung": 1, "score": 0.9,
      "citations": [ { "source": "Yen Ba Dieu Tau Ca", "locator": "cach cat" } ] } ],
  "interpretation": { "beginner": "... (cited)", "expert": "... (cited)", "recommendations": ["..."] },
  "citations": [ { "source": "Yen Ba Dieu Tau Ca", "locator": "cach cat", "han": "青龍返首" } ],
  "confidence": 0.72,
  "ai_disclosure": { "model": "gpt-4o-mini", "limits": "decision support, not a verdict; no medical/legal/financial advice", "review_status": "pending" },
  "created_at": "2026-07-08T12:00:05Z" }
```

## §9 - Open questions

- Whether to embed the full interactive chart or only the report's text chart summary. Default: render the `chart_summary` text region at P1 (it is copied into the report and always present); embed the interactive chart (TASK-CHART-001/002/003) by `query_id` as an additive enhancement, always read-only.
- How confidence is displayed. Default: a supporting band or short label next to the AIDisclosureBadge, never a headline percentage, so it informs without implying false precision; REPORT carries the number, the UI chooses the presentation (TASK-REPORT-001 s9).
- Where a pending report shows the HumanReviewGate: inline vs a banner. Default: mark the report not-yet-approved prominently and show the gate (TASK-RAG-004) where the reviewer acts; a plain reader sees the not-yet-approved state without the approve/reject controls.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Boundary erased | chart summary and interpretation in one undifferentiated block | forbidden; deterministic and interpreted regions are visually separated (strategy 4.4) |
| Missing disclosure | interpretation shown without the badge | forbidden; `AIDisclosureBadge` is mandatory; a test rejects its absence |
| Color-only polarity | cat/hung shown by color alone | forbidden; polarity is color + icon + text (TASK-WEB-001) |
| Pending looks approved | a `pending` report shown as final | mark not-yet-approved, distinct from approved |
| Client re-renders the PDF | the screen builds the file locally | forbidden; the PDF is the TASK-REPORT-002 export by `report_id` |
| Report mutated | the screen writes a report/chart field | forbidden; read-only; a byte-equality test asserts it |

## §11 - Notes

The report view is the last visible mile of the deterministic-and-AI boundary in a durable artifact (strategy 4.4): the engine's chart summary and detected patterns in one region, the AI's cited interpretation in another, physically separated, with the AIDisclosureBadge mandatory, the citations first-class, and a pending report marked as such. It renders the TASK-REPORT-001 object and asks TASK-REPORT-002 for the PDF - it neither assembles nor re-renders the file - and it keeps the report and any embedded envelope read-only. It is a SHOULD at P1 that lifts a single result into a saved, shareable, printable report without loosening one guardrail.
