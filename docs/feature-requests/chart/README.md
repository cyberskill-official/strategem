# CHART - interactive chart components

The interactive chart views that render each Tam Thuc la so: the 9-palace QiMen chart (the product's signature visual) first, then the LiuRen and TaiYi views, plus a shared export/accessibility pass. 4 FRs, ~48 engineering-hours, P0 flagship then P1-P2. Source of rationale: `../../strategy/tam-thuc-unified-plan-2026-07-08.md` (sections 4.3, 4.4) and Grok 34 (the chart) + 51 (the wireframes) + Claude 07 (the chart screen). Language is Next.js / TypeScript (DEC-2), rendered inside the FR-WEB-001 shell. Implementation order and trigger: `../IMPLEMENTATION_ORDER.md` + `../PROMPT.md`.

Every chart in this module is a pure view over the engine's output. It reads the la so envelope and never casts, re-derives, or "fixes up" a chart (strategy 4.3). The chart is a faithful picture of a deterministic computation an oracle verified, not a second engine and not an illustration.

## FRs

| FR | Pri | Phase | h | depends_on | Spec | Title |
|---|---|---|--:|---|---|---|
| CHART-001 | MUST | P0 | 16 | WEB-001, QMDG-006 | [FR-CHART-001](FR-CHART-001-nine-palace-qimen.md) | Interactive 9-palace QiMen chart (4 layers, hover/click, cat/hung color, export) |
| CHART-002 | MUST | P1 | 12 | CHART-001, LN-006 | [FR-CHART-002](FR-CHART-002-liuren-view.md) | LiuRen chart view (thien dia ban, tu khoa, tam truyen, thien tuong) |
| CHART-003 | SHOULD | P2 | 12 | CHART-001, TAT-006 | [FR-CHART-003](FR-CHART-003-taiyi-view.md) | TaiYi chart view (cuu cung, 16 than, tuong) |
| CHART-004 | SHOULD | P1 | 8 | CHART-001 | [FR-CHART-004](FR-CHART-004-export-a11y.md) | Chart export (PNG/SVG/print) + accessibility (dau chong test, screen reader) |

One P0 FR is authored: CHART-001, the interactive 9-palace QiMen chart. Three are authored: CHART-002 (the LiuRen chart view - thien dia ban / tu khoa / tam truyen / thien tuong, P1, needs LN-006), CHART-003 (the TaiYi chart view - cuu cung / 16 than / tuong, P2, needs TAT-006), and CHART-004 (the shared PNG/SVG/print export + the full accessibility pass including the dau chong stacked-diacritics test and screen-reader support, P1).

## Internal spine

```
WEB-001 + QMDG-006 -> CHART-001 (9-palace QiMen; establishes the "pure reader of ban" pattern + export seam)
   -> CHART-004 (export PNG/SVG/print + accessibility; completes the export seam)
   -> CHART-002 (LiuRen view; also needs LN-006)
   -> CHART-003 (TaiYi view; also needs TAT-006)
```

CHART-001 is the flagship and sets the pattern the other two views inherit: read the engine's `ban`, render the domain's native notation, encode no rule of your own.

## Cross-module dependencies

- Depends on WEB: every chart renders inside the FR-WEB-001 shell and uses its tokens and the cat/hung color+icon+text convention. Depends on the engines: CHART-001 reads the FR-QMDG-006 `KyMonBan` (`he = "ky_mon"`), CHART-002 reads the FR-LN-006 LiuRen `ban`, CHART-003 reads the FR-TAT-006 TaiYi `ban` - each is a pure reader of its engine's output.
- Blocks WEB: FR-WEB-003 (the results screen) embeds CHART-001; the report view (FR-WEB-005) and export (FR-REPORT-002) build on the chart export seam CHART-004 completes.
- Reads the FR-PLAT-002 envelope read-only: a chart never writes `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai`. The `ban` shape each view reads is pinned to its engine's assembly FR via a shared golden fixture, so a chart change is a reviewed, versioned envelope change (PLAT-002), not a silent view edit.

## Module notes

- Charts read the la so envelope only (strategy 4.3): the component's whole job is to render exactly what the engine placed in `ban` and the polarity in `cach_cuc`, including empty slots as empty (never fabricated). It computes nothing - the Luoshu center-palace lodging, the am/duong ban swaps, the tam truyen derivation, cach-cuc detection are all the engine's. Making the view a pure reader keeps the determinism guarantee from leaking into the UI; a read-only byte-equality test asserts the envelope is unchanged after render.
- cat/hung is never encoded by color alone: a favorable/unfavorable palace or lesson is marked by color AND an icon AND text together (FR-WEB-001). A color-only marker fails for color-blind users and in print, and a polarity is easy to over-read as a verdict, so it always carries an explicit icon and word. This is the module's most-repeated rule across all three views.
- Faithful notation is contract, not style: the fixed Luoshu arrangement (`4 9 2 / 3 5 7 / 8 1 6`), the four separated QiMen layers (dia ban / thien ban+cuu tinh / bat mon / bat than), the LiuRen thien-dia-ban and tam-truyen layout, and the TaiYi cuu-cung-and-16-than layout are the notations the domain reads; getting a position or a layer order wrong makes the chart unreadable to a practitioner. Each view is tested against a real golden envelope from its engine.
- SVG is the default renderer: crisp at any zoom, accessible (each palace/lesson a focusable node with a text alternative), and directly serializable for export (CHART-004). Responsiveness and the Vietnamese stacked-diacritics (dau chong) clip test are acceptance gates on every view, since domain labels carry Han plus diacritics.
