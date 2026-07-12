---
id: FR-CHART-002
title: "Interactive LiuRen chart view - renders the he=luc_nham ban: the thien dia ban (fixed dia ban 12-branch ring + rotating thien ban), tu khoa (four lessons), tam truyen (three transmissions), and the twelve thien tuong; hover/click detail; cat/hung by color + icon + text; reads the envelope, a pure reader"
module: CHART
priority: MUST
status: done
phase: P1
slice: 1
lang: typescript
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-34, Claude-02, strategy 4.3]
related_frs: [FR-WEB-001, FR-CHART-001, FR-WEB-003, FR-CHART-004, FR-PLAT-002, FR-LN-006, FR-STRAT-004]
depends_on: [FR-CHART-001, FR-LN-006]
blocks: []
new_paths:
  - apps/web/src/components/chart/liuren-chart.tsx
  - apps/web/src/components/chart/thien-dia-ban.tsx
  - apps/web/src/components/chart/tu-khoa.tsx
  - apps/web/src/components/chart/tam-truyen.tsx
  - apps/web/src/components/chart/thien-tuong-ring.tsx
  - apps/web/src/lib/chart/read-luc-nham-ban.ts
  - apps/web/tests/liuren-chart.test.tsx
---

## §1 - Description (BCP-14 normative)

This FR builds the interactive LiuRen (Dai Luc Nham) chart view - the second chart type, rendering the la so the LiuRen engine cast (FR-LN-006). Like the 9-palace QiMen chart (FR-CHART-001), it is a pure view over the engine's output: it reads the la so envelope and never computes or mutates it (strategy 4.3). It inherits the FR-CHART-001 pattern - read the engine's `ban`, render the domain's native notation, encode no rule of its own. It owns the LiuRen rendering and interaction; it does NOT cast the chart (FR-LN-006) and does NOT own the results/cross-system composition (FR-WEB-003, FR-STRAT-004) that embeds it.

The component SHALL read the la so envelope (FR-PLAT-002) for `he = "luc_nham"`, taking the `ban` slot as the LiuRen `ban` (FR-LN-006) and the top-level `cach_cuc` for polarity. It SHALL render, in the LiuRen native notation: (1) the thien dia ban - the fixed dia ban 12-branch ring (地盤, the twelve dia chi in their fixed positions) with the rotating thien ban ring (天盤) placed over it by the nguyet tuong; (2) the tu khoa (四課, four lessons), each as its upper/lower (thuong / ha) can-chi pair with the khac direction (thuong khac 上剋 / ha khac 下剋) marked; (3) the tam truyen (三傳, three transmissions) - so truyen (初傳), trung truyen (中傳), mat truyen (末傳) - each with its chi, its thien tuong, and its luc than; and (4) the twelve thien tuong (十二天將, the heavenly generals) placed around the board thuan/nghich from the khoi quy nhan. Where a slot is empty (e.g. the degenerate phuc ngam / phan ngam cases the engine produced), it SHALL render empty, not fabricated.

Hover or click on a board cell, a lesson, a transmission, or a general SHALL reveal a detail view (its full content and role). Elements carrying a cach cuc / polarity SHALL be marked cat / hung / trung by color AND icon AND text - never color alone (FR-WEB-001). The chart SHALL be responsive and SHALL expose the export seam (FR-CHART-004 completes export/print/accessibility) and meet baseline accessibility (keyboard-reachable cells, text alternatives). It SHALL treat the envelope as read-only and SHALL NOT write `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai`.

## §2 - Why this design (rationale for humans)

A LiuRen reading is read in a fixed order through a fixed notation: the caster looks at the thien dia ban, reads the four lessons, follows the three transmissions, and weighs the twelve generals (Claude-02). That order and that notation are the domain's language, so getting the fixed dia ban ring, the thien-ban rotation, the four-lesson layout, or the transmission order wrong makes the chart unreadable to anyone who practices the art. Rendering exactly the `ban` the engine produced - including the degenerate phuc ngam / phan ngam cases as the engine cast them, empty where empty - keeps the chart an honest picture of a deterministic computation the kinliuren oracle verified (FR-LN-006), not an illustration that smooths over an awkward cast.

Making the view a pure reader is the same architectural boundary the QiMen chart rests on (strategy 4.3, FR-CHART-001 s2). LiuRen has the most explicit, least school-contested rules of the three engines - the nine tong mon are a decision tree, the tam truyen derivation is the engine's - so the temptation to "help" by re-deriving a transmission in the view is real and must be refused: the moment the chart re-computes a truyen, it asserts something the engine did not, and the determinism guarantee leaks into the UI. cat/hung by color plus icon plus text is the accessibility floor applied where a favorable/unfavorable general or lesson is easy to over-read as a verdict, so it always carries an explicit icon and word, and survives grayscale print.

## §3 - Contract (data / layout / interaction)

### Input (reads the FR-PLAT-002 envelope, he = luc_nham)

```ts
// the LiuRen ban shape (FR-LN-006), read-only
type LucNhamBan = {
  thien_dia_ban: {
    dia_ban: string[];        // [Chi;12] fixed earth ring: 子丑寅卯辰巳午未申酉戌亥
    thien_ban: string[];      // [Chi;12] heaven ring placed over dia_ban by nguyet tuong
    nguyet_tuong: string;     // the month-general that sets the rotation
  };
  tu_khoa: KhoaItem[];        // [KhoaItem;4] four lessons
  tam_truyen: TruyenItem[];   // [so, trung, mat] three transmissions, in order
  thien_tuong: Record<string, string>;  // 12 generals keyed by the branch they sit on
  khoi_quy_nhan: string;      // the quy nhan (day/night) that seeds the general placement
};
type KhoaItem = { thuong: string; ha: string; khac: "thuong_khac" | "ha_khac" | null };  // upper/lower + khac direction
type TruyenItem = { chi: string; thien_tuong: string; luc_than: string };
function readLucNhamBan(laso: LaSo): { ban: LucNhamBan; cachCuc: CachCuc[] };  // validates he === "luc_nham"
```

### Layout (LiuRen native notation)

```
thien dia ban:  outer ring = dia ban (fixed 子..亥), inner ring = thien ban (rotated by nguyet tuong)
tu khoa:        [ khoa 1 ][ khoa 2 ][ khoa 3 ][ khoa 4 ]   each: thuong over ha, khac marked
tam truyen:     so (初) / trung (中) / mat (末), top to bottom, each: chi + thien tuong + luc than
thien tuong:    the 12 generals placed on the branches they occupy (thuan/nghich from khoi quy nhan)
```

### The twelve thien tuong (十二天將)

Quy Nhan 貴人, Dang Xa 螣蛇, Chu Tuoc 朱雀, Luc Hop 六合, Cau Tran 勾陳, Thanh Long 青龍, Thien Khong 天空, Bach Ho 白虎, Thai Thuong 太常, Huyen Vu 玄武, Thai Am 太陰, Thien Hau 天后. The view renders each on the branch the engine placed it on (`thien_tuong` map); it does not compute the placement.

### Interaction and cat/hung marking

Hover/click a board cell, a lesson, a transmission, or a general -> a detail showing its full content and role. An element referenced by a `cach_cuc` is marked cat / hung / trung as color + icon + text together (semantic tokens from FR-WEB-001; never color alone). Cells, lessons, transmissions, and generals are keyboard-focusable and the detail is keyboard-reachable.

## §4 - Acceptance criteria

1. Given a `he = "luc_nham"` envelope, the component renders the thien dia ban with the fixed dia ban 12-branch ring and the thien ban rotated over it by the nguyet tuong.
2. It renders the tu khoa (four lessons) with each lesson's thuong/ha pair and the khac direction (thuong khac / ha khac) marked, and the tam truyen in order (so / trung / mat) each with its chi, thien tuong, and luc than.
3. It renders the twelve thien tuong on the branches the engine placed them on; it computes no placement, and empty/degenerate slots (phuc ngam / phan ngam) render blank, never fabricated.
4. Hover and click reveal a detail with the full content and role; cells, lessons, transmissions, and generals are keyboard-focusable and the detail is keyboard-reachable.
5. Elements carrying a cach cuc show cat/hung/trung with color AND icon AND text (never color alone), using the FR-WEB-001 semantic tokens.
6. The chart is responsive from a narrow (phone) to a wide (desktop) viewport without overlap or clipping, including stacked Vietnamese diacritics (FR-WEB-001 clip test); it exposes the export seam FR-CHART-004 completes.
7. The component treats the envelope as read-only (no write to `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`).

## §5 - Verification

- `tests/liuren-chart.test.tsx`: renders a `LucNhamBan` fixture from a real FR-LN-006 golden envelope; asserts the fixed dia ban ring and the thien-ban rotation, the four lessons with thuong/ha + khac, the tam truyen order and each truyen's chi/thien tuong/luc than, the twelve generals on their branches, empty-slot handling for a phuc/phan ngam fixture, the cat/hung color+icon+text on a `cach_cuc`-named element, and the read-only invariant (envelope byte-identical after render).
- Interaction: hover/click opens the detail with the right content; keyboard focus traverses cells/lessons/transmissions/generals and opens detail.
- Responsive + a11y: layout holds at phone and desktop widths; `jest-axe` clean; elements have text alternatives; the diacritics clip test passes over the labels (Han + phien am).
- Contract: `LucNhamBan` is checked against the FR-LN-006 shape via a shared golden fixture; a drift fails the test.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `lib/chart/read-luc-nham-ban.ts`: read `ban` (as `LucNhamBan`) and top-level `cach_cuc`; validate `he === "luc_nham"`.
2. `thien-dia-ban.tsx`: the fixed dia ban outer ring + the thien ban inner ring rotated by nguyet tuong.
3. `tu-khoa.tsx` + `tam-truyen.tsx`: the four lessons (thuong/ha + khac) and the three transmissions in order (chi + thien tuong + luc than); empty slots blank.
4. `thien-tuong-ring.tsx`: the twelve generals on the branches the engine placed them on.
5. `liuren-chart.tsx`: compose the board, lessons, transmissions, and generals (SVG); responsive sizing; cat/hung marking from `cach_cuc` with color+icon+text; the FR-CHART-001 export seam.
6. `tests/liuren-chart.test.tsx` with the FR-LN-006 golden fixture.

## §7 - Dependencies

Depends on FR-CHART-001 (the "pure reader of its engine's `ban`" pattern, the export seam, and the cat/hung color+icon+text convention) and FR-LN-006 (the LiuRen `ban` and the `he = "luc_nham"` envelope it reads). Uses FR-WEB-001 (tokens, semantic markers, the shell it renders inside). Embedded by FR-WEB-003 (results) and FR-STRAT-004 (cross-system validate renders LiuRen alongside QiMen). Completed by FR-CHART-004 (export/print/accessibility builds on the export seam). Reads the FR-PLAT-002 envelope read-only (strategy 4.3); the `LucNhamBan` contract is pinned to FR-LN-006 via a shared golden fixture.

## §8 - Example payloads

```ts
// the component reads charts[i] from the QueryResponse (he = "luc_nham")
const { ban, cachCuc } = readLucNhamBan(chart);
// ban.thien_dia_ban.nguyet_tuong = "登明"; dia_ban = ["子","丑",...,"亥"] (fixed); thien_ban rotated over it
// ban.tu_khoa[0] = { thuong: "寅", ha: "子", khac: "ha_khac" }
// ban.tam_truyen = [ { chi:"寅", thien_tuong:"青龍", luc_than:"..." }, { ... }, { ... } ]  // so / trung / mat
// ban.thien_tuong = { "寅":"青龍", "子":"神后/天后", ... }   // generals on their branches
// cachCuc = [ ... ]  // any detected khoa the / cach; polarity shown as color + icon + text
```

## §9 - Open questions

- How to depict the thien-ban rotation over the fixed dia ban on a small screen. Default: two concentric rings on desktop (dia ban outer fixed, thien ban inner rotated); on a phone keep the rings but let the detail carry the full pairing on tap, so nothing is fabricated or dropped, only relocated (the FR-CHART-001 progressive-reveal rule).
- How much LiuRen semantics the view encodes vs leaves to the engine. Default: the view renders exactly what `LucNhamBan` contains (the rings, the four lessons, the three transmissions, the generals, the khac marks) and encodes no rule - the nguyet-tuong rotation, the tu-khoa khac test, the nine-tong-mon transmission derivation, and the general placement are all FR-LN-006's. The chart is a faithful picture, not a second engine.
- Whether to show luc than and khoa the inline or only in the detail. Default: show the core notation (rings, lessons, transmissions, generals) inline and carry luc than / khoa the into the detail, keeping the board legible while nothing is hidden.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Wrong ring / order | dia ban not fixed, thien ban mis-rotated, or transmissions out of order | forbidden; the fixed dia ban and the engine's rotation/order are tested against a golden fixture |
| Fabricated slot | a degenerate phuc/phan ngam slot rendered as filled | forbidden; an empty slot renders blank; the view never invents a lesson/transmission/general |
| View recomputes | the chart derives a truyen or a general placement | forbidden; pure reader of `ban`; read-only envelope; a byte-equality test asserts it |
| Color-only cat/hung | polarity shown by color alone | forbidden; cat/hung is color + icon + text (FR-WEB-001) |
| Clipped on mobile | responsive layout overlaps/clips the rings or diacritics | the responsive + diacritics-clip tests fail; fix before ship |
| Envelope-shape drift | `LucNhamBan` differs from FR-LN-006 | the shared golden-fixture contract test fails; treat any `ban` change as a versioned FR-PLAT-002 change |

## §11 - Notes

The LiuRen view is the second chart type and it inherits the FR-CHART-001 discipline exactly: faithful notation (the fixed dia ban ring, the thien-ban rotation, the four lessons with khac, the three transmissions in order, the twelve generals on their branches, empty where empty) and no computation (it reads `ban` and `cach_cuc` and writes nothing - strategy 4.3, asserted by a read-only test). cat/hung is color + icon + text, never color alone. The export seam is exposed here and completed by FR-CHART-004, and the `LucNhamBan` contract stays pinned to FR-LN-006 via a shared golden fixture, so a chart change is a reviewed, versioned envelope change, not a silent view edit.
