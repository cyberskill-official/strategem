---
id: FR-WEB-007
title: "Management flow - saved-chart history, a per-system school-flag (co_truong_phai) configuration UI stamped onto each new chart, and share/export"
module: WEB
priority: SHOULD
status: ready_to_implement
phase: P2
slice: 1
lang: typescript
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s6, strategy 4.3, Grok-35]
related_frs: [FR-WEB-003, FR-WEB-002, FR-API-004, FR-PLAT-002, FR-QMDG-006, FR-LN-006, FR-TAT-006, FR-CHART-004, FR-REPORT-002, FR-LEGAL-001]
depends_on: [FR-WEB-003]
blocks: []
new_paths:
  - apps/web/src/app/manage/history/page.tsx
  - apps/web/src/app/manage/settings/page.tsx
  - apps/web/src/components/manage/history-list.tsx
  - apps/web/src/components/manage/school-flags-form.tsx
  - apps/web/src/components/manage/share-dialog.tsx
  - apps/web/src/components/manage/export-menu.tsx
  - apps/web/src/lib/api/history.ts
  - apps/web/src/lib/flags/school-flags.ts
  - apps/web/tests/management-flow.test.tsx
---

## §1 - Description (BCP-14 normative)

This FR builds the management flow - the third product flow (Claude-07 s6, strategy 1): the surface where a user manages their own body of work rather than casting or learning. It has three parts: a saved-chart history list, a school-flag (`co_truong_phai`) configuration UI where an advanced user sets the conventions their charts are cast under, and share/export. It owns these management screens; it does NOT cast a chart (FR-WEB-002 / the gateway) and does NOT itself render the engine plates - it lists, configures, shares, and exports what the platform already produced.

The flow SHALL provide: (a) a history list of the user's saved charts (from FR-API-004, by `query_id`), filterable by system and question type, each linking to its results (FR-WEB-003) or report (FR-WEB-005); (b) a school-flag configuration UI (`school-flags-form`) where an advanced user sets `co_truong_phai` per system - for QiMen `dingju_method`, `pan_method`, and `yin_yang_pan`; for LiuRen `khoi_quy_nhan`; for TaiYi `epoch` - plus the shared calendar flags (`co_lich_phap`: `use_true_solar_time`, `zi_hour_day_rollover`, `late_zi_handling`, `truong_sinh_phai`, `delta_t_model`), with the engine defaults shown as defaults; and (c) share (a link to a chart/report) and export (PDF via FR-REPORT-002, PNG/SVG via FR-CHART-004). The configured flags SHALL be carried into the next cast as the `co_truong_phai` / `co_lich_phap` overrides (FR-WEB-002), so that every new chart is stamped with the conventions it was cast under and remains reproducible from `dau_vao` plus flags (strategy 4.3, FR-PLAT-002). The UI SHALL set flags but SHALL NOT cast - the engine stamps and casts. It SHALL present schools fairly: no school is marked "correct", each flag documents its options and its default (strategy 7). It reads persisted charts read-only and SHALL NOT mutate `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai` on an existing chart.

## §2 - Why this design (rationale for humans)

School flags are the technical expression of a cultural fact: QiMen alone has three orthogonal convention axes (dinh-cuc method, chuyen/phi ban, am/duong ban) that change the chart, and practitioners of different schools reject each other's charts (FR-PLAT-002 s2, RISK-2). The management flow is where a serious user makes those conventions explicit and their own - setting the flags once, so every chart they cast is stamped with, and reproducible from, the school they practice. Exposing the full flag surface here rather than in the primary cast form (FR-WEB-002 s9 deferred it here) keeps the everyday casting screen simple - defaults for most - while giving the advanced user a real, honest configuration surface. Presenting the flags with their options and defaults, and never labeling one school "correct", is the cultural-fairness rule made into a form (strategy 7).

The history list matters because a chart's value compounds over time: a user revisits a cast to compare its reading against what actually happened, which is the reflective decision-support use the product is positioned for (strategy 7, Claude-07 s2). Share and export exist so that reflection can leave the app - a report handed to a colleague, a chart printed for a notebook - which is why export goes through the backend PDF (FR-REPORT-002) and the chart's own export seam (FR-CHART-004) rather than a client re-render, keeping the exported artifact faithful and its cat/hung markers icon-plus-text, not color-only. Setting flags but never casting keeps the deterministic boundary intact: the UI declares the conventions, the engine stamps and casts, and reproducibility is preserved.

## §3 - Contract (screens / flags / data)

### Screens (Claude-07 s6, on the FR-WEB-001 shell)

- `/manage/history` - the saved-chart list (`history-list`), filter by system / question type, each row linking to `/results/{query_id}` (FR-WEB-003) or the report (FR-WEB-005), with per-row share/export.
- `/manage/settings` - the `school-flags-form`: the per-system `co_truong_phai` and the shared `co_lich_phap`, each flag with its options and its documented default.

### School flags (`lib/flags/school-flags.ts`, stamped into `co_truong_phai` / `co_lich_phap`)

| System | Flag | Options (default first) |
|---|---|---|
| QiMen (ky_mon) | `dingju_method` | `chaibu` \| `zhirunzhuo` ... |
| QiMen | `pan_method` | `zhuan` \| `fei` |
| QiMen | `yin_yang_pan` | `duong` \| `am` |
| LiuRen (luc_nham) | `khoi_quy_nhan` | day/night quy nhan selection (default the Mao..Than window) |
| TaiYi (thai_at) | `epoch` | `kim_kinh` \| `co_dien` (+ reduction method) |
| shared calendar | `use_true_solar_time` | `true` \| `false` |
| shared calendar | `zi_hour_day_rollover` | `23:00` \| ... |
| shared calendar | `late_zi_handling` | `tao_zi` \| ... |
| shared calendar | `truong_sinh_phai` | `ngu_hanh` \| ... |
| shared calendar | `delta_t_model` | `espenak_meeus` \| ... |

The option sets are the engines' closed enums (FR-QMDG-006, FR-LN-006, FR-TAT-006, FR-CORE-005 / FR-PLAT-002); the form renders the enum, not a free-text field, so an invalid flag cannot be set. The default is always shown as the default.

### Data (`lib/api/history.ts`)

```ts
async function getHistory(filter?: { he?: string; question_type?: string }): Promise<ChartRef[]>;  // FR-API-004, read-only
async function shareChart(queryId: string): Promise<{ url: string }>;
type SchoolConfig = { co_truong_phai: Record<string, string>; co_lich_phap: Record<string, string> };
function toCastOverrides(cfg: SchoolConfig): { co_truong_phai: Record<string, string> };  // carried into FR-WEB-002
```

Export uses FR-REPORT-002 (PDF, by `report_id`) and FR-CHART-004 (PNG/SVG, from the chart's export seam); the flow triggers them, it does not render the files itself.

## §4 - Acceptance criteria

1. The history list shows the user's saved charts (FR-API-004) filterable by system and question type, each linking to its results (FR-WEB-003) or report (FR-WEB-005), with per-row share/export.
2. The school-flag form exposes the full per-system `co_truong_phai` (QiMen `dingju_method`/`pan_method`/`yin_yang_pan`, LiuRen `khoi_quy_nhan`, TaiYi `epoch`) and the shared `co_lich_phap`, each as its engine enum (not free text), each showing its default.
3. The configured flags are carried into the next cast (FR-WEB-002) as `co_truong_phai` / `co_lich_phap` overrides, so a new chart is stamped with them and reproducible from `dau_vao` plus flags (strategy 4.3).
4. No school is marked "correct"; each flag documents its options and default (fair presentation, strategy 7).
5. Share returns a link; export triggers the FR-REPORT-002 PDF and the FR-CHART-004 PNG/SVG, not a client re-render; exported cat/hung stays icon + text, never color alone.
6. The flow sets flags but never casts a chart itself, and never mutates `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai` on an existing persisted chart (read-only, asserted).

## §5 - Verification

- `tests/management-flow.test.tsx`: renders a history fixture and asserts the filters and the results/report links; asserts the flag form renders the per-system enums with defaults and produces a `SchoolConfig`; asserts `toCastOverrides` hands `co_truong_phai` to a stubbed FR-WEB-002 cast; asserts no "correct school" labeling; asserts share returns a link and export calls FR-REPORT-002 / FR-CHART-004 (stubs); asserts the read-only invariant on an existing chart.
- Contract: `ChartRef` against FR-API-004; the flag enums against the FR-QMDG-006 / FR-LN-006 / FR-TAT-006 / FR-PLAT-002 flag sets (shared fixtures); a drift fails the test.
- Accessibility: `jest-axe` clean; keyboard-operable filters, form, and menus; the stacked-diacritics clip test (FR-WEB-001) over flag labels and question types.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/api/history.ts`: `getHistory(filter)` (FR-API-004, read-only) and `shareChart(queryId)`.
2. `components/manage/history-list.tsx`: the filterable saved-chart list with results/report links and per-row share/export.
3. `lib/flags/school-flags.ts` + `components/manage/school-flags-form.tsx`: the per-system `co_truong_phai` and shared `co_lich_phap` as engine enums with defaults; `toCastOverrides`.
4. `share-dialog.tsx` + `export-menu.tsx`: the share link and the export triggers (FR-REPORT-002 PDF, FR-CHART-004 PNG/SVG).
5. `app/manage/history/page.tsx` + `app/manage/settings/page.tsx`: the two screens in the FR-WEB-001 shell; carry `SchoolConfig` into FR-WEB-002.
6. `tests/management-flow.test.tsx` + the shared flag-enum and FR-API-004 fixtures.

## §7 - Dependencies

Depends on FR-WEB-003 (the results presentation the history links to, and the read-only chart discipline). Reads FR-API-004 (persisted chart references and the saved flag) and stamps flags whose enums are owned by FR-QMDG-006, FR-LN-006, FR-TAT-006, and FR-CORE-005 / FR-PLAT-002; the configured flags feed FR-WEB-002's cast as `co_truong_phai` / `co_lich_phap`. Export uses FR-REPORT-002 (PDF) and FR-CHART-004 (PNG/SVG); links to FR-WEB-005 (report view). Uses FR-LEGAL-001 for the disclaimer. It sets conventions but never casts (strategy 4.2) and never mutates an existing chart's envelope (strategy 4.3).

## §8 - Example payloads

```ts
// the advanced user's school configuration, stamped onto each new cast
const cfg: SchoolConfig = {
  co_truong_phai: { dingju_method: "chaibu", pan_method: "zhuan", yin_yang_pan: "duong" },  // QiMen
  co_lich_phap:  { use_true_solar_time: "true", zi_hour_day_rollover: "23:00",
                   late_zi_handling: "tao_zi", truong_sinh_phai: "ngu_hanh", delta_t_model: "espenak_meeus" }
};
toCastOverrides(cfg);  // -> { co_truong_phai: { dingju_method: "chaibu", pan_method: "zhuan", yin_yang_pan: "duong" } }
// carried into FR-WEB-002 so the next chart is cast and stamped under these conventions (reproducible; strategy 4.3)
```

```json
// a history row (FR-API-004), read-only
{ "query_id": "q_8a1", "he": "luc_nham", "question_type": "hon_nhan", "cast_at": "2026-07-07T15:40:00Z", "saved": true }
```

## §9 - Open questions

- Whether flags are a single global profile or per-system profiles. Default: a per-system section within one settings screen (QiMen / LiuRen / TaiYi / shared calendar), since a user may practice one school of QiMen and the common LiuRen defaults; one form, grouped by system.
- Share scope: a private link vs a public read-only page. Default: an authenticated share link at P2 (the recipient must sign in), given birth data and question text are sensitive (RISK-5); a public share is a later, consent-gated feature.
- Whether changing flags re-casts existing charts. Default: no - existing charts are immutable and stamped with the flags they were cast under; a flag change only affects future casts, keeping every saved chart reproducible from its own stamped flags (strategy 4.3).

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Flow casts a chart | the settings screen computes a chart | forbidden; it sets flags; the engine stamps and casts (FR-WEB-002 / gateway) |
| Unstamped convention | a flag set in the UI is not carried into the cast | forbidden; `toCastOverrides` hands the flags to FR-WEB-002 so the chart stamps them (reproducibility) |
| Free-text flag | a flag rendered as a free-text field | forbidden; flags are the engines' closed enums; the form renders the enum |
| "Correct school" labeling | one school marked authoritative | forbidden; schools presented fairly with options + default (strategy 7) |
| Client re-renders export | the flow builds the PDF/PNG locally | forbidden; export is FR-REPORT-002 / FR-CHART-004; cat/hung stays icon + text |
| Existing chart mutated | a flag change rewrites a saved chart | forbidden; saved charts are immutable and read-only; changes affect only future casts |

## §11 - Notes

The management flow is where a user's own body of work lives: the history to revisit, the school flags to make their conventions explicit and their own, and share/export to let a chart leave the app. Its load-bearing rule is that it configures but never casts - the UI declares `co_truong_phai` / `co_lich_phap`, and the engine stamps and casts, so every chart stays reproducible from `dau_vao` plus its stamped flags (strategy 4.3, FR-PLAT-002). Flags are the engines' closed enums, schools are presented fairly (strategy 7), export goes through the backend so exported charts keep their icon-plus-text polarity, and saved charts are immutable. It is a SHOULD at P2, the third flow that turns the product from a caster into a workbench.
