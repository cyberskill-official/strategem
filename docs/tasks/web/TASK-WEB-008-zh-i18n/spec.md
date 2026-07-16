---
id: TASK-WEB-008
title: "Chinese (ZH) locale + RTL-ready layout scaffolding - adds the zh message catalog on the WEB-006 foundation and makes the layout direction-agnostic (CSS logical properties) so a future RTL locale needs no relayout"
module: WEB
priority: COULD
status: done
phase: P3
slice: 1
lang: typescript
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s4.3, strategy 7, Grok-40]
related_frs: [TASK-WEB-006, TASK-WEB-001, TASK-KB-003, TASK-RAG-003]
depends_on: [TASK-WEB-006]
blocks: []
new_paths:
  - apps/web/src/messages/zh.json
  - apps/web/src/lib/i18n/direction.ts
  - apps/web/src/styles/logical.css
  - apps/web/tests/zh-i18n.test.tsx
  - apps/web/tests/rtl-ready.test.tsx
---

## §1 - Description (BCP-14 normative)

This task extends the i18n foundation (TASK-WEB-006) with a third locale, Chinese (`zh`), and makes the layout direction-agnostic so a future right-to-left (RTL) locale can be added without re-laying-out any screen. It does two things and no more: it adds the `zh` UI-chrome catalog and registers `zh` in the locale set, and it converts the layout from physical (left/right) to logical (inline-start/inline-end) so direction becomes a single attribute, not a per-component rewrite. It reuses TASK-WEB-006's two-plane split unchanged - it adds a locale and a direction axis, it does not add a second i18n mechanism.

The frontend SHALL add `zh` to the next-intl locale set (`["vi", "en", "zh"]`, `vi` still default) with a `messages/zh.json` UI-chrome catalog. Domain content in `zh` SHALL be served pre-translated from the backend exactly as in TASK-WEB-006 - the UI SHALL NOT machine-translate a classical term - and because the classical source script IS Han, for `zh` the KB three-layer store's Han layer (TASK-KB-003) SHALL be surfaced as the primary domain text rather than a transliteration. The layout SHALL be made RTL-ready: components SHALL use CSS logical properties (`margin-inline`, `padding-inline`, `inset-inline`, `text-align: start/end`, `border-inline`) instead of physical `left`/`right`, and the document direction SHALL be driven by a single `dir` attribute derived from the active locale (`dir("zh") = ltr`; the scaffolding admits an RTL locale returning `rtl` with no further layout change). RTL-readiness is scaffolding and a test gate, not a shipped RTL locale; the acceptance is that adding one would need no relayout, proven by a mirrored-direction snapshot.

## §2 - Why this design (rationale for humans)

Chinese is the special case that proves the TASK-WEB-006 split was right: the tradition's source text is Han, so for a Chinese reader the classical passage is not something to translate into - it is the primary text (Claude-07 s4.3, strategy 7). Surfacing the Han layer directly for `zh`, rather than a romanized or re-translated form, is the most faithful rendering the product can offer, and it falls straight out of the two-plane design - chrome from the catalog, domain content (here, the Han itself) from the knowledge base. Adding `zh` is therefore mostly a catalog plus a rule about which layer is primary, not a new system, which is exactly why TASK-WEB-006 is its dependency and its foundation.

RTL-readiness is done now, cheaply, as scaffolding, because retrofitting direction after a dozen screens have hardcoded `left`/`right` is expensive and error-prone, while writing logical properties from the start costs almost nothing. The product has no RTL locale today, so this task does not ship one; it removes the structural blocker so that if an Arabic or Hebrew locale is ever wanted, it is a catalog plus a `dir` value, not a layout project. Keeping this a COULD at P3 reflects that: it is the hardening-phase polish that makes the internationalization foundation complete and future-proof, not an MVP need.

## §3 - Contract (locale / direction / logical layout)

### Locale set (extends TASK-WEB-006 `routing.ts`)

```ts
export const routing = defineRouting({
  locales: ["vi", "en", "zh"],   // zh added here; vi still default
  defaultLocale: "vi",
  localePrefix: "as-needed"
});
```

`messages/zh.json` is the UI-chrome catalog (same shape as `vi.json`/`en.json`). Domain content in `zh` is fetched from the backend as in TASK-WEB-006; the resolver is unchanged.

### Domain content for zh (Han is primary)

| Locale | Primary domain text | Layers shown |
|---|---|---|
| vi | dich (Vietnamese rendering) | Han + bach thoai + dich |
| en | expert English rendering | Han + english |
| zh | the Han source (chu Han) | Han (primary) + bach thoai |

For `zh`, `domain-content.ts` (TASK-WEB-006) returns the Han layer as `text`; it still never machine-translates.

### Direction (`lib/i18n/direction.ts`, `styles/logical.css`)

```ts
function dir(locale: string): "ltr" | "rtl" {
  // vi | en | zh -> ltr; the scaffolding admits a future rtl locale -> "rtl"
}
```

`logical.css` and the components use logical properties only: `margin-inline`, `padding-inline`, `inset-inline-start/end`, `border-inline`, `text-align: start/end`. The `<html dir>` is set from `dir(locale)`. No component uses physical `left`/`right` for layout flow.

## §4 - Acceptance criteria

1. `zh` is in the locale set (`["vi","en","zh"]`, `vi` default) with a `messages/zh.json` chrome catalog; switching to `zh` renders the chrome from that catalog.
2. Domain content in `zh` is served pre-translated from the backend (TASK-KB-003 / TASK-RAG-003) and never machine-translated in the UI; for `zh` the Han layer is surfaced as the primary domain text.
3. The layout uses CSS logical properties (no physical `left`/`right` for layout flow), and `<html dir>` is driven by `dir(locale)`.
4. RTL-readiness is proven by a mirrored-direction (forced `rtl`) snapshot/test that shows the layout mirrors correctly with no per-component change - even though no RTL locale ships.
5. The TASK-WEB-006 two-plane split is unchanged: chrome from catalogs, domain content from the backend resolver; the Han is preserved in every locale.

## §5 - Verification

- `tests/zh-i18n.test.tsx`: asserts `zh` in the locale set; renders the shell in `zh` and asserts chrome from `messages/zh.json`; asserts a `zh` domain term surfaces the Han layer as primary and is not machine-translated (spy asserts no translate call); asserts the Han is present.
- `tests/rtl-ready.test.tsx`: asserts no component uses physical `left`/`right` for layout flow (a style audit over the layout properties); forces `dir="rtl"` and asserts the layout mirrors via logical properties (a mirrored snapshot) with no component edit.
- Accessibility: `lang="zh"` and the correct `dir`; the stacked-diacritics clip test (TASK-WEB-001) still passes for `vi`; Han renders at the chart/label sizes without clipping.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. Extend `i18n/routing.ts` with `zh`; add `messages/zh.json` (chrome).
2. `lib/i18n/direction.ts`: `dir(locale)` returning `ltr` for vi/en/zh and admitting a future `rtl`; set `<html dir>` from it.
3. Rule in `domain-content.ts` (TASK-WEB-006): for `zh`, return the Han layer as the primary `text`; still no translate path.
4. `styles/logical.css` + a sweep of the TASK-WEB-001/002/003 layout to logical properties (`margin-inline`, `padding-inline`, `inset-inline`, `text-align: start/end`).
5. `tests/zh-i18n.test.tsx` + `tests/rtl-ready.test.tsx` (including the forced-`rtl` mirrored snapshot).

## §7 - Dependencies

Depends on TASK-WEB-006 (the next-intl foundation, the two-plane split, and the domain-content resolver it extends - `zh` is a locale plus a primary-layer rule, not a new mechanism). Reads `zh` domain content from TASK-KB-003 (the Han/bach thoai layers) and TASK-RAG-003 (any `zh` interpretation), served pre-translated. Uses TASK-WEB-001's shell and clip test. It ships no RTL locale; it removes the structural blocker so one could be added as a catalog plus a `dir` value.

## §8 - Example payloads

```ts
// zh surfaces the Han layer as primary; still never machine-translated
const p = await getDomainContent("pattern", "qimen_thanh_long_hoi_dau", "zh");
// -> { han: "青龍返首", text: "青龍返首", locale: "zh", source: "Yen Ba Dieu Tau Ca" }  // Han is the primary text

dir("zh");  // "ltr"    dir("vi"); // "ltr"    // scaffolding admits a future rtl locale -> "rtl"
```

```css
/* logical, not physical - so a future rtl locale mirrors with no relayout */
.panel { padding-inline: var(--space-4); margin-inline-start: var(--space-2); text-align: start; }
```

## §9 - Open questions

- Whether `zh` distinguishes Traditional vs Simplified. Default: follow the KB source - the classical text is Traditional Han; `zh` surfaces it as stored, and a Simplified variant is a later KB concern, not a UI transform (the UI never converts the script).
- Whether to ship an actual RTL locale now. Default: no - this task proves RTL-readiness with a forced-`rtl` test only; shipping an RTL locale waits for real demand and its own expert-translated content.
- Bidi handling where Han/Latin and (future) RTL text mix. Default: rely on the browser's Unicode bidi with `dir` set correctly and logical properties; revisit isolation (`bdi`) only if a real RTL locale lands.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Machine-translated zh term | UI translates a classical term into/within zh | forbidden; domain content is pre-translated; for zh the Han layer is primary |
| Physical left/right | a component hardcodes `left`/`right` for flow | forbidden; logical properties only; the rtl-ready audit fails |
| Direction not mirrored | forced `rtl` breaks the layout | the mirrored-direction test fails; fix with logical properties, not per-component hacks |
| Second i18n mechanism | zh added outside next-intl / the TASK-WEB-006 split | forbidden; zh is a locale + primary-layer rule on the existing foundation |
| Han converted | UI transforms Traditional to Simplified (or romanizes) | forbidden; the Han is surfaced as stored; the UI never converts the script |

## §11 - Notes

TASK-WEB-008 completes the internationalization story: Chinese as a third locale where the Han source text is itself the primary domain content (the case that vindicates the TASK-WEB-006 two-plane split), plus RTL-ready scaffolding that makes direction a single attribute rather than a future relayout. It adds a locale and a direction axis on top of TASK-WEB-006 - not a second i18n system - keeps the domain-content resolver translate-free, and preserves the Han in every locale. It is a COULD at P3: hardening-phase polish that future-proofs the foundation without shipping an RTL locale before there is content for one.
