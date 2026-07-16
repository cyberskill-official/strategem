---
id: TASK-CHART-001
title: "Interactive 9-palace QiMen chart - SVG/Canvas Luoshu grid, four layers per palace (dia ban / thien ban+cuu tinh / bat mon / bat than), hover/click palace detail, cat/hung by color + icon + text, responsive, exportable; reads the la so ban for he=ky_mon"
module: CHART
priority: MUST
status: done
phase: P0
slice: 1
lang: typescript
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-34, Grok-51, Claude-07, strategy 4.3]
related_frs: [TASK-WEB-001, TASK-QMDG-006, TASK-WEB-003, TASK-CHART-004, TASK-PLAT-002, TASK-CHART-002, TASK-CHART-003]
depends_on: [TASK-WEB-001, TASK-QMDG-006]
blocks: [TASK-WEB-003, TASK-CHART-004, TASK-CHART-002, TASK-CHART-003]
new_paths:
  - apps/web/src/components/chart/nine-palace-chart.tsx
  - apps/web/src/components/chart/palace.tsx
  - apps/web/src/components/chart/palace-detail.tsx
  - apps/web/src/components/chart/layers.tsx
  - apps/web/src/components/chart/luoshu-layout.ts
  - apps/web/src/lib/chart/read-ky-mon-ban.ts
  - apps/web/src/lib/chart/export.ts
  - apps/web/tests/nine-palace-chart.test.tsx
---

## §1 - Description (BCP-14 normative)

This task builds the interactive 9-palace (cuu cung) QiMen chart - the signature visual of the product and the centerpiece of every wireframe (Grok-34, Grok-51). It renders the QiMen la so as an interactive Luoshu grid with the four QiMen plates per palace, and it is a pure view over the engine's output: it reads the la so envelope and never computes or mutates it (strategy 4.3). It owns the chart rendering and interaction; it does NOT cast the chart (TASK-QMDG-006) and does NOT own the results-screen composition (TASK-WEB-003), which embeds this component.

The component SHALL read the la so envelope (TASK-PLAT-002) for `he = "ky_mon"`, taking the `ban` slot as the `KyMonBan` (TASK-QMDG-006) and the top-level `cach_cuc` for palace polarity. It SHALL render the nine palaces in the fixed Luoshu arrangement (`4 9 2 / 3 5 7 / 8 1 6`, palace 5 = Trung, center) using SVG (preferred) or Canvas. Each palace SHALL show its four layers, clearly distinguished: (1) dia ban (the earth-plate stem), (2) thien ban plus cuu tinh (the heaven-plate stem and the nine star), (3) bat mon (the eight gate), (4) bat than (the eight spirit). Where a palace has no gate or spirit (the `Option` is empty in `KyMonBan`), that layer SHALL render empty, not fabricated. Truc phu (the acting star) and truc su (the acting gate) SHALL be visually marked.

Hover or click on a palace SHALL reveal a palace-detail view (its four layers in full, its cach cuc, and its role). Palaces carrying a cach cuc SHALL be marked with cat/hung status shown by color AND an icon AND text - never color alone (TASK-WEB-001). The chart SHALL be responsive (usable from a phone to a wide desktop) and exportable; the full export/print/accessibility pass is TASK-CHART-004, and this task SHALL expose the export seam and meet the baseline accessibility (keyboard-reachable palaces, text alternatives). The component SHALL treat the envelope as read-only and SHALL NOT write `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai`.

## §2 - Why this design (rationale for humans)

The 9-palace chart is how a QiMen reading is actually read: a practitioner scans the Luoshu grid palace by palace, layer by layer, and the whole product's positioning around strategic timing and direction (strategy 3.4) is expressed through it. So the fixed Luoshu arrangement and the four clearly separated layers are not stylistic - they are the notation the domain uses, and getting the palace positions or the layer order wrong makes the chart unreadable to anyone who knows the art. Rendering exactly the `KyMonBan` the engine produced, including empty gate/spirit slots as empty (never invented), is what keeps the chart honest: it is a faithful picture of a deterministic computation, not an illustration.

Making the component a pure reader of the envelope is the same architectural boundary the rest of the platform rests on (strategy 4.3). The chart shows facts the engine computed and an oracle verified; the moment the view could re-derive or "fix up" a palace, it would be asserting something the engine did not, and the determinism guarantee would leak into the UI. Cat/hung by color plus icon plus text (never color alone) is the accessibility floor applied where it matters most: a favorable/unfavorable marker read only by red/green fails for color-blind users and in print, and a polarity is easy to over-read as a verdict, so it carries an explicit icon and word.

## §3 - Contract (data / layout / interaction)

### Input (reads the TASK-PLAT-002 envelope, he = ky_mon)

```ts
// the KyMonBan shape (TASK-QMDG-006), read-only
type KyMonBan = {
  dinh_cuc: { duong_don: boolean; so_cuc: number; tiet_khi: string; tam_nguyen: string };
  dia_ban:  Record<string, string>;      // earth-plate stems by palace
  thien_ban: string[];                    // [Can; 9] heaven-plate stems
  cuu_tinh:  string[];                    // [CuuTinh; 9] nine stars
  bat_mon:   (string | null)[];           // [Option<BatMon>; 9] eight gates
  bat_than:  (string | null)[];           // [Option<BatThan>; 9] eight spirits
  truc_phu:  string;                      // acting star
  truc_su:   string;                      // acting gate
};
function readKyMonBan(laso: LaSo): { ban: KyMonBan; cachCuc: CachCuc[] };  // reads ban + top-level cach_cuc
```

### Luoshu layout (`luoshu-layout.ts`)

```
palace grid (fixed):   4  9  2
                       3  5  7      // 5 = Trung (center)
                       8  1  6
```

Each palace maps to its index into the `[..;9]` arrays. Palace 5 (Trung) is the center; the center-palace lodging rule is the engine's (TASK-QMDG-006), and the view renders whatever the engine placed there.

### The four layers per palace (`layers.tsx`)

| Layer | Content | Source field |
|---|---|---|
| 1 dia ban | earth-plate stem | `dia_ban[palace]` |
| 2 thien ban + cuu tinh | heaven-plate stem + nine star | `thien_ban[i]`, `cuu_tinh[i]` |
| 3 bat mon | eight gate (may be empty) | `bat_mon[i]` |
| 4 bat than | eight spirit (may be empty) | `bat_than[i]` |

Truc phu and truc su are marked on the palaces holding them. Empty `bat_mon`/`bat_than` slots render blank.

### Interaction and cat/hung marking

Hover/click a palace -> `palace-detail` shows the four layers in full plus the palace's cach cuc and role. A palace referenced by a `cach_cuc[].cung` is marked with its polarity: cat / hung / trung, shown as color + icon + text together (semantic tokens from TASK-WEB-001; never color alone). Palaces are keyboard-focusable and the detail is reachable by keyboard.

### Export seam (`export.ts`)

Exposes the render for TASK-CHART-004 (PNG/SVG/print). At P0 this task provides the SVG serialization hook and text alternatives; TASK-CHART-004 completes the export, print stylesheet, and the full screen-reader pass.

## §4 - Acceptance criteria

1. Given a `he = "ky_mon"` envelope, the component renders nine palaces in the fixed Luoshu arrangement (`4 9 2 / 3 5 7 / 8 1 6`, 5 center), each mapped to the correct array index.
2. Each palace shows the four layers - dia ban / thien ban+cuu tinh / bat mon / bat than - visually distinguished; empty gate/spirit slots render blank, never fabricated.
3. Truc phu and truc su are visually marked on their palaces.
4. Hover and click reveal a palace detail with the full four layers, the palace's cach cuc, and its role; palaces are keyboard-focusable and the detail is keyboard-reachable.
5. Palaces carrying a cach cuc show cat/hung with color AND icon AND text (never color alone), using the TASK-WEB-001 semantic tokens.
6. The chart is responsive from a narrow (phone) to a wide (desktop) viewport without overlap or clipping, including stacked Vietnamese diacritics (TASK-WEB-001 clip test).
7. The component treats the envelope as read-only (no write to `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`) and exposes the export seam TASK-CHART-004 completes.

## §5 - Verification

- `tests/nine-palace-chart.test.tsx`: renders a `KyMonBan` fixture (from a real TASK-QMDG-006 golden envelope); asserts palace-to-index mapping for the Luoshu grid, the four layers per palace, empty-slot handling, the truc phu/truc su marks, the cat/hung color+icon+text on the palace named by a `cach_cuc.cung`, and the read-only invariant (envelope byte-identical after render).
- Interaction: hover/click opens the palace detail with the right content; keyboard focus traverses palaces and opens detail.
- Responsive + a11y: layout holds at phone and desktop widths; `jest-axe` clean; palaces have text alternatives; the diacritics clip test passes over palace labels.
- Contract: the `KyMonBan` type is checked against the TASK-QMDG-006 shape via a shared golden fixture; a drift fails the test.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/chart/read-ky-mon-ban.ts`: read `ban` (as `KyMonBan`) and top-level `cach_cuc` from the envelope; validate `he === "ky_mon"`.
2. `luoshu-layout.ts`: the fixed palace grid and the palace-index map.
3. `palace.tsx` + `layers.tsx`: a palace cell with the four layers; empty gate/spirit slots blank; truc phu/truc su marks.
4. `nine-palace-chart.tsx`: the SVG Luoshu grid composing nine palaces; responsive sizing; cat/hung marking from `cach_cuc[].cung` with color+icon+text.
5. `palace-detail.tsx`: the hover/click detail (four layers + cach cuc + role); keyboard reachable.
6. `export.ts`: the SVG serialization/export seam for TASK-CHART-004; `tests/nine-palace-chart.test.tsx` with the golden fixture.

## §7 - Dependencies

Depends on TASK-WEB-001 (the tokens, the semantic color+icon+text convention for cat/hung, and the shell it renders inside) and TASK-QMDG-006 (the `KyMonBan` and the `he = "ky_mon"` envelope it reads). Blocks TASK-WEB-003 (the results screen embeds this chart) and TASK-CHART-004 (export/print/accessibility builds on the export seam). Sets the pattern TASK-CHART-002 (LiuRen view) and TASK-CHART-003 (TaiYi view) follow: each is a pure reader of its engine's `ban`. Reads the TASK-PLAT-002 envelope read-only (strategy 4.3).

## §8 - Example payloads

```ts
// the component reads charts[0] from the QueryResponse (he = "ky_mon")
const { ban, cachCuc } = readKyMonBan(charts[0]);
// ban.dinh_cuc = { duong_don: true, so_cuc: 1, tiet_khi: "冬至", tam_nguyen: "thuong" }
// ban.truc_phu = "天蓬"; ban.truc_su = "休門"
// cachCuc = [ { id: "qimen_thanh_long_hoi_dau", name: "青龍返首", cung: 1, polarity: "cat" } ]
// -> palace 1 (bottom-middle in the Luoshu grid) is marked cat with an icon + the word "cat" + the cat color token
```

## §9 - Open questions

- SVG vs Canvas. Default: SVG - crisp at any zoom, accessible (each palace a focusable node with a text alternative), and directly serializable for the TASK-CHART-004 export; Canvas is a fallback only if a future animation or very large grid needs it. The four-layer legibility and the a11y requirement favor SVG.
- How much QiMen semantics the view encodes vs leaves to the engine. Default: the view renders exactly what `KyMonBan` contains (positions, stems, stars, gates, spirits, truc phu/su, and the polarity from `cach_cuc`) and encodes no QiMen rule itself - the center-palace lodging, the am/duong ban swaps, and cach-cuc detection are all the engine's (TASK-QMDG-006). The chart is a faithful picture, not a second engine.
- Layer density on small screens: all four layers always vs a progressive reveal. Default: show all four on desktop; on a phone, keep the grid but let the palace detail carry the full four layers on tap, so nothing is fabricated or dropped - only relocated to the detail.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Wrong palace positions | Luoshu grid mis-mapped | forbidden; the fixed `4 9 2 / 3 5 7 / 8 1 6` map is tested against a golden fixture |
| Fabricated layer | empty gate/spirit rendered as filled | forbidden; an empty `Option` renders blank; the view never invents a placement |
| View recomputes | chart derives/fixes a palace | forbidden; pure reader of `ban`; read-only envelope; a byte-equality test asserts it |
| Color-only cat/hung | polarity shown by color alone | forbidden; cat/hung is color + icon + text (TASK-WEB-001) |
| Clipped on mobile | responsive layout overlaps/clips | the responsive + diacritics-clip tests fail; fix before ship |
| Envelope-shape drift | `KyMonBan` differs from TASK-QMDG-006 | the shared golden-fixture contract test fails; treat any `ban` change as a TASK-PLAT-002 versioned change |

## §11 - Notes

This is the product's signature visual and a pure reader of the engine's output, so two rules govern it: the notation must be faithful (the fixed Luoshu arrangement, the four separated layers in order, empty slots blank, truc phu/su marked) and the component must never compute (it reads `ban` and `cach_cuc` and writes nothing - strategy 4.3, asserted by a read-only test). cat/hung is color + icon + text, never color alone. The export seam is exposed here and completed by TASK-CHART-004; the same "pure reader of its engine's `ban`" pattern is what TASK-CHART-002 (LiuRen) and TASK-CHART-003 (TaiYi) inherit. Keep the `KyMonBan` contract pinned to TASK-QMDG-006 via a shared golden fixture so a chart change is a reviewed, versioned envelope change, not a silent view edit.
