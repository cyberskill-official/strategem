---
id: TASK-CHART-004
title: "Chart export and accessibility - PNG/SVG/print export for all chart types (QiMen/LiuRen/TaiYi), the Vietnamese stacked-diacritics (dau chong) clip test at 100/200/400%, screen-reader labels for palaces and components, and cat/hung never encoded by color alone"
module: CHART
priority: SHOULD
status: done
phase: P1
slice: 1
lang: typescript
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s5, Grok-34, strategy 4.4]
related_frs: [TASK-CHART-001, TASK-WEB-001, TASK-CHART-002, TASK-CHART-003, TASK-REPORT-002, TASK-WEB-005, TASK-WEB-007]
depends_on: [TASK-CHART-001]
blocks: []
new_paths:
  - apps/web/src/lib/chart/export-png.ts
  - apps/web/src/lib/chart/export-svg.ts
  - apps/web/src/components/chart/export-controls.tsx
  - apps/web/src/styles/chart-print.css
  - apps/web/src/lib/chart/a11y-labels.ts
  - apps/web/tests/chart-export.test.tsx
  - apps/web/tests/chart-a11y.test.tsx
---

## §1 - Description (BCP-14 normative)

This task completes the chart export seam TASK-CHART-001 exposed and delivers the full accessibility pass for every chart type. It is the shared, cross-cutting slice: it takes the SVG serialization hook each chart provides (QiMen TASK-CHART-001, LiuRen TASK-CHART-002, TaiYi TASK-CHART-003) and turns it into PNG, SVG, and print export, and it makes every chart pass the Vietnamese stacked-diacritics (dau chong) clip test and be fully screen-reader navigable. It owns export and accessibility for charts; it does NOT render the chart internals (each chart task does) and does NOT re-cast or read the envelope beyond what the chart already read.

The module SHALL provide, for all chart types via their common export seam: (a) SVG export - direct serialization of the rendered chart, crisp at any zoom; (b) PNG export - a raster of the same at a specified scale; and (c) print - a print stylesheet (`chart-print.css`) that lays the chart to a page, collapses any opt-in glass to a solid surface (TASK-WEB-001), and preserves every marker. The clip test SHALL run over each chart's palace/lesson/than labels (Han plus stacked Vietnamese diacritics) at 100% / 200% / 400% zoom on both light and dark themes, and no diacritic or descender SHALL be clipped (TASK-WEB-001). Every chart component - each palace, lesson, transmission, than, and general - SHALL carry a screen-reader label naming its content and role (`a11y-labels.ts`), so the chart is navigable and announced without sight of the visual. cat/hung / trung polarity SHALL never be encoded by color alone - every polarity marker SHALL pair color with an icon and text - and this SHALL hold in every export: a PNG, an SVG, and a print output SHALL each carry the icon and text, not color only, so the marker survives grayscale, print, and low vision.

## §2 - Why this design (rationale for humans)

Export and accessibility are done once, as a shared slice, because they are the same job across all three charts: each chart already exposes an SVG seam and already renders cat/hung as icon-plus-text, so the export and the a11y pass belong in one place rather than re-implemented three times. Putting them together is deliberate - export and accessibility are the same underlying requirement seen twice. A chart that is truly accessible (each element labeled, nothing color-only) is also a chart that exports faithfully (the labels and the icon-plus-text markers survive into the PNG, the SVG, and the printed page). Building them apart would let one drift from the other.

The dau chong clip test is a first-class gate here for the same reason it is in TASK-WEB-001: the product's primary language is Vietnamese, its charts are dense with Han plus stacked tone-and-vowel marks, and those marks are the first thing a tight line-height clips - most visibly at the 200% and 400% zoom a low-vision user relies on (Claude-07 s5.1). Screen-reader labels for palaces and components make the signature visual usable by a blind practitioner, which a purely visual chart never could be. And the never-color-alone rule matters most in export: a chart printed in grayscale or read by a screen reader must still convey cat from hung, so the icon and word travel with the color into every output - the accessibility floor and the export fidelity are one requirement (strategy 4.4).

## §3 - Contract (export / print / accessibility)

### Export (`lib/chart/export-svg.ts`, `lib/chart/export-png.ts`)

```ts
// consumes the TASK-CHART-001 export seam each chart type exposes (QiMen / LiuRen / TaiYi)
function exportSvg(chartEl: SVGSVGElement): string;                 // serialized SVG (fonts + markers inlined)
async function exportPng(chartEl: SVGSVGElement, scale?: number): Promise<Blob>;   // raster at scale (default 2x)
// both preserve every cat/hung marker as color + icon + text; neither re-reads or re-casts the envelope.
```

Export works for all chart types because each renders through the common seam; a new chart type is exportable the moment it exposes the seam, with no change here.

### Print (`styles/chart-print.css`)

A `@media print` stylesheet that fits the chart to the page, collapses opt-in glass to a solid surface (TASK-WEB-001), preserves the icon+text polarity markers, and keeps Han plus diacritics unclipped at print scale.

### Accessibility (`lib/chart/a11y-labels.ts`)

| Requirement | Rule |
|---|---|
| labeled components | every palace / lesson / transmission / than / general has a screen-reader label naming its content and role |
| keyboard | every component is focusable and its detail is keyboard-reachable (baseline from each chart task; completed here) |
| dau chong clip test | palace/label text (Han + stacked diacritics) unclipped at 100/200/400% on light + dark |
| never color alone | cat/hung/trung is color + icon + text, in the UI and in every export (PNG/SVG/print) |

## §4 - Acceptance criteria

1. SVG, PNG, and print export are available for all chart types (QiMen/LiuRen/TaiYi) through the common TASK-CHART-001 export seam; a chart type is exportable via the seam with no per-type export code.
2. The dau chong stacked-diacritics clip test passes over each chart's palace/label text (Han + diacritics) at 100% / 200% / 400% zoom on light and dark themes; no diacritic or descender is clipped.
3. Every chart component (palace / lesson / transmission / than / general) carries a screen-reader label naming its content and role; the chart is keyboard-navigable and announced.
4. cat/hung/trung is never color alone - every polarity marker pairs color with an icon and text - in the UI and in the PNG, SVG, and print outputs (a grayscale export still distinguishes polarity).
5. Print collapses opt-in glass to a solid surface and keeps the chart and its markers unclipped at print scale.
6. Export does not re-cast or re-read the envelope beyond what the chart already rendered; it serializes the rendered chart only.

## §5 - Verification

- `tests/chart-export.test.tsx`: exports a rendered QiMen, LiuRen, and TaiYi chart to SVG and PNG through the common seam; asserts the serialized output contains the icon+text polarity markers (not color-only) and the labels; asserts a forced-grayscale render still distinguishes cat from hung; asserts print collapses glass to solid.
- `tests/chart-a11y.test.tsx`: `jest-axe` clean on each chart; asserts every palace/lesson/than/general has a screen-reader label and role; asserts keyboard traversal reaches every component and its detail; runs the dau chong clip test at 100/200/400% on light + dark over Han + diacritic labels.
- Cross-type: the export and a11y tests run over all three chart types via the shared seam, so a new chart type inherits the gate.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/chart/export-svg.ts`: serialize the chart's SVG through the TASK-CHART-001 seam, inlining fonts and the icon+text markers.
2. `lib/chart/export-png.ts`: raster the serialized SVG at a scale (default 2x); preserve markers.
3. `styles/chart-print.css`: the `@media print` layout - fit to page, glass to solid, markers and diacritics preserved.
4. `lib/chart/a11y-labels.ts`: the label/role builder for every chart component (palace/lesson/transmission/than/general).
5. `components/chart/export-controls.tsx`: the export menu (SVG / PNG / print) wired to the seam.
6. `tests/chart-export.test.tsx` + `tests/chart-a11y.test.tsx` run across QiMen/LiuRen/TaiYi.

## §7 - Dependencies

Depends on TASK-CHART-001 (the export seam and the baseline accessibility it exposes; this task completes both). Applies to TASK-CHART-002 (LiuRen) and TASK-CHART-003 (TaiYi) through the same seam, so all three chart types export and pass the a11y gate uniformly. Uses TASK-WEB-001 (the tokens, the glass-collapses-on-print rule, the cat/hung color+icon+text convention, and the shared clip-test harness). The export it completes is what the report view (TASK-WEB-005), the PDF export (TASK-REPORT-002), and the management-flow export (TASK-WEB-007) build on for chart images. It re-reads no envelope and re-casts nothing (strategy 4.3) - it serializes the rendered chart.

## §8 - Example payloads

```ts
// export any chart type through the common TASK-CHART-001 seam
const svg = exportSvg(chartEl);              // "<svg ...>...</svg>" with icon+text markers inlined
const png = await exportPng(chartEl, 2);     // 2x PNG Blob; cat/hung still icon + text (survives grayscale)

// a11y label for a QiMen palace carrying a cat cach cuc (icon + text, not color-only)
labelFor(palace);
// -> "Cung 1: dia ban 戊, thien ban 天蓬, cua 休門, than 值符. Cach 青龍返首, tinh chat: cat."
```

```css
/* chart-print.css - glass collapses to solid, markers preserved, nothing clipped */
@media print {
  .cs-surface-glass { backdrop-filter: none; background: var(--surface-solid); }
  .chart { break-inside: avoid; }
}
```

## §9 - Open questions

- PNG rasterization approach: canvas `drawImage` of the serialized SVG vs a headless render. Default: serialize the SVG (fonts and markers inlined) and raster via canvas client-side at MVP; a server-side headless render is an option only if font/diacritic fidelity needs it, and it must reuse the same serialization so the icon+text markers are identical.
- Whether print is per-chart or whole-report. Default: this task owns the chart print stylesheet; the whole-report PDF is TASK-REPORT-002, which embeds the chart export - one chart-export source of truth, two consumers.
- How verbose the screen-reader labels are. Default: name the component, its key contents, its role, and its polarity as icon+text-equivalent words; keep it a concise, ordered reading of the palace/lesson rather than a dump, so a screen-reader user can scan the chart.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Color-only in export | a PNG/SVG/print marker conveys polarity by color alone | forbidden; every export carries the icon + text; a grayscale-export test asserts cat vs hung |
| Diacritic clipped | a label clips a stacked mark at 100/200/400% | forbidden; the dau chong clip test fails on light+dark; fix line/height before ship |
| Unlabeled component | a palace/than/general has no screen-reader label | forbidden; every component has a label + role; axe + a label test assert it |
| Glass survives print | opt-in glass renders on the printed page | forbidden; print collapses glass to a solid surface (TASK-WEB-001) |
| Export re-casts | the exporter re-reads / recomputes the chart | forbidden; it serializes the rendered chart only; no envelope re-read |
| Per-type export drift | one chart type exports differently | forbidden; all types export through the common seam; the cross-type tests assert parity |

## §11 - Notes

TASK-CHART-004 completes the export seam TASK-CHART-001 opened and delivers the accessibility pass for all three chart types at once, because export and accessibility are one requirement seen twice: a chart whose every component is labeled and whose polarity is icon-plus-text is also a chart that exports faithfully to PNG, SVG, and print, grayscale and screen-reader included. The dau chong clip test at 100/200/400% on light and dark is a gate, not a nicety (Claude-07 s5.1), and the never-color-alone rule holds into every export (strategy 4.4). It re-reads no envelope and re-casts nothing - it serializes the rendered chart - and the export it finishes is what TASK-WEB-005, TASK-REPORT-002, and TASK-WEB-007 build on for chart images.
