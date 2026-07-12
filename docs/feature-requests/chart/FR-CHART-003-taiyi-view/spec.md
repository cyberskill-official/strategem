---
id: FR-CHART-003
title: "Interactive TaiYi chart view - renders the he=thai_at ban: the nine palaces (cuu cung), the Thai At star position, the sixteen than, and the generals (bat tuong); hover/click detail; cat/hung by color + icon + text; reads the envelope, a pure reader"
module: CHART
priority: SHOULD
status: done
phase: P2
slice: 1
lang: typescript
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-34, Claude-04, strategy 4.3]
related_frs: [FR-WEB-001, FR-CHART-001, FR-WEB-003, FR-CHART-004, FR-PLAT-002, FR-TAT-006, FR-STRAT-004]
depends_on: [FR-CHART-001, FR-TAT-006]
blocks: []
new_paths:
  - apps/web/src/components/chart/taiyi-chart.tsx
  - apps/web/src/components/chart/cuu-cung-taiyi.tsx
  - apps/web/src/components/chart/thai-at-marker.tsx
  - apps/web/src/components/chart/muoi-sau-than-ring.tsx
  - apps/web/src/components/chart/bat-tuong.tsx
  - apps/web/src/lib/chart/read-thai-at-ban.ts
  - apps/web/tests/taiyi-chart.test.tsx
---

## §1 - Description (BCP-14 normative)

This FR builds the interactive TaiYi (Thai At Than So) chart view - the third chart type, rendering the la so the TaiYi engine cast (FR-TAT-006). Like the QiMen (FR-CHART-001) and LiuRen (FR-CHART-002) views, it is a pure view over the engine's output: it reads the la so envelope and never computes or mutates it (strategy 4.3), and it inherits the FR-CHART-001 pattern - read the engine's `ban`, render the domain's native notation, encode no rule of its own. It owns the TaiYi rendering and interaction; it does NOT cast the chart (FR-TAT-006) and does NOT own the composition (FR-WEB-003, FR-STRAT-004) that embeds it.

The component SHALL read the la so envelope (FR-PLAT-002) for `he = "thai_at"`, taking the `ban` slot as the TaiYi `ban` (FR-TAT-006) and the top-level `cach_cuc` for polarity. It SHALL render, in the TaiYi native notation: (1) the nine palaces (cuu cung), noting that Thai At skips the center palace (5) and lodges in Khon (2) - the view renders whatever palace the engine placed each element in; (2) the Thai At star position, visually marked on its palace; (3) the sixteen than (十六神) placed on the 16-position ring, distinguishing chinh cung (正宮) from gian than (間神); and (4) the generals - the bat tuong (八將) and the computed toan positions (chu toan / khach toan 主算/客算, Van Xuong 文昌, Thuy Kich 始擊, ke than 計神) - marked where the engine placed them. Where a slot is empty it SHALL render empty, not fabricated.

Hover or click on a palace, the Thai At marker, a than, or a general SHALL reveal a detail view (its full content and role). Elements carrying a cach cuc / polarity (tam tai, truong/doan toan, chu-khach outcome markers) SHALL be marked cat / hung / trung by color AND icon AND text - never color alone (FR-WEB-001). The chart SHALL be responsive and SHALL expose the export seam (FR-CHART-004 completes export/print/accessibility) and meet baseline accessibility. It SHALL treat the envelope as read-only and SHALL NOT write `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai`.

## §2 - Why this design (rationale for humans)

A TaiYi chart is read off the nine palaces with the Thai At star, the sixteen-than ring, and the generals - and two of its notation rules are exactly the ones a naive rendering gets wrong: Thai At skips the center palace and lodges in Khon (2), and the 16-than ring distinguishes chinh cung from gian than (FR-TAT-006, Claude-04). Rendering exactly what the engine placed - never "correcting" a palace, never collapsing the chinh cung / gian than distinction - keeps the chart an honest picture of a deterministic computation the kintaiyi oracle verified. TaiYi's determinism starts from tich nien, a large integer count, and the engine already did that arithmetic; the view's job is to show the result, not to redo any part of it.

Making the view a pure reader is the same boundary the other two charts rest on (strategy 4.3), and it carries extra weight here because TaiYi speaks to large matters - national fortune, long cycles - where an over-confident presentation is most harmful (Claude-04 s6.3). So the chart shows the engine's facts and leaves the chu-khach victory reading to the AI layer (which is cited and AIDisclosure-labeled); the chart itself never editorializes. cat/hung by color plus icon plus text is the accessibility floor applied where a favorable/unfavorable toan or a tam-tai marker is easy to over-read as a verdict, so it always carries an explicit icon and word and survives grayscale print - the module's most-repeated rule across all three views.

## §3 - Contract (data / layout / interaction)

### Input (reads the FR-PLAT-002 envelope, he = thai_at)

```ts
// the TaiYi ban shape (FR-TAT-006), read-only
type ThaiAtBan = {
  cuu_cung: PalaceCell[];        // the nine palaces; Thai At lodges Khon (2), skips center (5)
  thai_at: { cung: number };     // the Thai At star palace
  muoi_sau_than: ThanItem[];     // [16] the sixteen than on the ring
  bat_tuong: TuongItem[];        // the eight generals
  toan: { chu_toan: number; khach_toan: number; van_xuong?: number; thuy_kich?: number; ke_than?: number };
  epoch: string;                 // the stamped tich-nien epoch (from co_truong_phai)
};
type PalaceCell = { cung: number; noi_dung: string[] };   // whatever the engine placed in the palace
type ThanItem = { vi_tri: number; ten: string; loai: "chinh_cung" | "gian_than" };  // 正宮 vs 間神
type TuongItem = { ten: string; cung: number };
function readThaiAtBan(laso: LaSo): { ban: ThaiAtBan; cachCuc: CachCuc[] };  // validates he === "thai_at"
```

### Layout (TaiYi native notation)

```
cuu cung:      3x3 palace grid; Thai At lodges Khon (2), skips center (5) - render as the engine placed
thai at:       marked on ban.thai_at.cung
16 than ring:  16 positions around the palaces; chinh cung (正宮) vs gian than (間神) distinguished
bat tuong:     the 8 generals on their palaces; the toan (chu/khach toan, Van Xuong, Thuy Kich, ke than) marked
```

### The sixteen than and the generals

The 16-than ring alternates chinh cung (on-palace) and gian than (between-palace) positions; the view renders each `than` at the `vi_tri` and with the `loai` the engine assigned, never re-deriving the counting. The bat tuong and the toan positions are rendered where the engine placed them (`bat_tuong`, `toan`); the chu-toan vs khach-toan strength comparison is a fact the engine computed, shown as a marker, not judged by the view.

### Interaction and cat/hung marking

Hover/click a palace, the Thai At marker, a than, or a general -> a detail with its full content and role. An element referenced by a `cach_cuc` (tam tai, truong/doan toan, chu-khach markers) is marked cat / hung / trung as color + icon + text together (FR-WEB-001; never color alone). Palaces, than, and generals are keyboard-focusable and the detail is keyboard-reachable.

## §4 - Acceptance criteria

1. Given a `he = "thai_at"` envelope, the component renders the nine palaces as the engine placed them (Thai At in Khon (2), center (5) skipped where the engine did so), and marks the Thai At star on `ban.thai_at.cung`.
2. It renders the sixteen than on the ring with each than's position and its chinh cung / gian than kind, and the bat tuong plus the toan positions (chu/khach toan, Van Xuong, Thuy Kich, ke than) where the engine placed them; it computes no placement.
3. Empty slots render blank, never fabricated; the view re-derives no counting (no chinh cung / gian than recount, no toan recompute).
4. Hover and click reveal a detail with the full content and role; palaces, than, and generals are keyboard-focusable and the detail is keyboard-reachable.
5. Elements carrying a cach cuc show cat/hung/trung with color AND icon AND text (never color alone), using the FR-WEB-001 semantic tokens.
6. The chart is responsive from a narrow (phone) to a wide (desktop) viewport without overlap or clipping, including stacked Vietnamese diacritics (FR-WEB-001 clip test); it exposes the export seam FR-CHART-004 completes.
7. The component treats the envelope as read-only (no write to `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`).

## §5 - Verification

- `tests/taiyi-chart.test.tsx`: renders a `ThaiAtBan` fixture from a real FR-TAT-006 golden envelope; asserts the nine-palace placement (Thai At in Khon, center skipped), the Thai At marker, the sixteen than with chinh cung / gian than, the bat tuong and toan positions, empty-slot handling, the cat/hung color+icon+text on a `cach_cuc`-named element, and the read-only invariant (envelope byte-identical after render).
- Interaction: hover/click opens the detail with the right content; keyboard focus traverses palaces/than/generals and opens detail.
- Responsive + a11y: layout holds at phone and desktop widths; `jest-axe` clean; elements have text alternatives; the diacritics clip test passes over the labels (Han + phien am).
- Contract: `ThaiAtBan` is checked against the FR-TAT-006 shape via a shared golden fixture; a drift fails the test.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/chart/read-thai-at-ban.ts`: read `ban` (as `ThaiAtBan`) and top-level `cach_cuc`; validate `he === "thai_at"`.
2. `cuu-cung-taiyi.tsx` + `thai-at-marker.tsx`: the nine-palace grid as the engine placed it, with the Thai At star marked on its palace.
3. `muoi-sau-than-ring.tsx`: the sixteen than on the ring with chinh cung / gian than distinguished.
4. `bat-tuong.tsx`: the eight generals and the toan positions (chu/khach toan, Van Xuong, Thuy Kich, ke than) where the engine placed them.
5. `taiyi-chart.tsx`: compose the palaces, Thai At, than ring, and generals (SVG); responsive; cat/hung marking from `cach_cuc` with color+icon+text; the FR-CHART-001 export seam.
6. `tests/taiyi-chart.test.tsx` with the FR-TAT-006 golden fixture.

## §7 - Dependencies

Depends on FR-CHART-001 (the "pure reader of its engine's `ban`" pattern, the export seam, and the cat/hung color+icon+text convention) and FR-TAT-006 (the TaiYi `ban` and the `he = "thai_at"` envelope it reads). Uses FR-WEB-001 (tokens, semantic markers, the shell). Embedded by FR-WEB-003 (results) and FR-STRAT-004 (cross-system validate adds TaiYi as a third opinion). Completed by FR-CHART-004 (export/print/accessibility builds on the export seam). Reads the FR-PLAT-002 envelope read-only (strategy 4.3); the `ThaiAtBan` contract is pinned to FR-TAT-006 via a shared golden fixture.

## §8 - Example payloads

```ts
// the component reads charts[i] from the QueryResponse (he = "thai_at")
const { ban, cachCuc } = readThaiAtBan(chart);
// ban.thai_at.cung = 2 (Khon; center palace 5 skipped)
// ban.muoi_sau_than[0] = { vi_tri: 1, ten: "太乙", loai: "chinh_cung" }
// ban.bat_tuong = [ { ten: "文昌", cung: 8 }, ... ]; ban.toan = { chu_toan: 12, khach_toan: 9, ... }
// cachCuc = [ ... ]  // tam tai / truong-doan toan / chu-khach markers; polarity shown as color + icon + text
```

## §9 - Open questions

- How to lay out the 16-than ring around a 3x3 palace grid on a small screen. Default: the ring around the grid on desktop; on a phone keep the grid and carry the than ring into a companion strip / the detail on tap, so nothing is fabricated or dropped, only relocated (the FR-CHART-001 progressive-reveal rule).
- How prominently to show the chu-toan vs khach-toan comparison. Default: show both toan as positional markers/values and leave the "who wins" reading to the AI layer (cited, AIDisclosure-labeled), since TaiYi speaks to large matters and the chart must not editorialize (Claude-04 s6.3).
- Whether to surface the stamped epoch on the chart. Default: show the `epoch` (from `co_truong_phai`) as chart metadata, since a 60-year epoch gap re-casts the whole chart and a reader should see which convention this chart was cast under (reproducibility, FR-PLAT-002).

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Wrong lodging | Thai At rendered in the center or a "corrected" palace | forbidden; render the engine's placement (Khon (2), center (5) skipped); tested against a golden fixture |
| Miscounted than | chinh cung / gian than distinction collapsed or recounted | forbidden; render each than's engine-assigned position and kind; the view never recounts |
| Fabricated slot | an empty palace/than/general rendered as filled | forbidden; empty renders blank; the view invents nothing |
| View recomputes | the chart re-derives a toan or a placement | forbidden; pure reader of `ban`; read-only envelope; a byte-equality test asserts it |
| Chart editorializes | the view asserts a chu-khach winner | forbidden; the chart shows facts; the victory reading is the cited AI layer's (Claude-04 s6.3) |
| Color-only cat/hung | polarity shown by color alone | forbidden; cat/hung is color + icon + text (FR-WEB-001) |

## §11 - Notes

The TaiYi view is the third chart type and it inherits the FR-CHART-001 discipline: faithful notation (the nine palaces as placed, Thai At lodged in Khon with the center skipped, the sixteen than with chinh cung / gian than kept distinct, the generals and toan where the engine placed them, empty where empty) and no computation (it reads `ban` and `cach_cuc` and writes nothing - strategy 4.3, asserted by a read-only test). Because TaiYi speaks to large matters, the chart shows facts and never editorializes the chu-khach outcome; that reading is the cited AI layer's. cat/hung is color + icon + text, never color alone. The export seam is exposed here and completed by FR-CHART-004, and the `ThaiAtBan` contract stays pinned to FR-TAT-006 via a shared golden fixture.
