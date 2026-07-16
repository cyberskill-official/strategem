---
id: TASK-WEB-006
title: "i18n foundation - next-intl with Vietnamese default and English, splitting UI labels (message catalogs) from domain content (patterns and interpretation text served pre-translated from KB/RAG); classical Han terms are never machine-translated"
module: WEB
priority: MUST
status: done
phase: P1
slice: 1
lang: typescript
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s4.3, strategy 7, Grok-40]
related_frs: [TASK-WEB-001, TASK-WEB-002, TASK-WEB-003, TASK-WEB-008, TASK-KB-003, TASK-RAG-003, TASK-LEGAL-001]
depends_on: [TASK-WEB-001]
blocks: [TASK-WEB-008]
new_paths:
  - apps/web/src/i18n/request.ts
  - apps/web/src/i18n/routing.ts
  - apps/web/src/messages/vi.json
  - apps/web/src/messages/en.json
  - apps/web/src/components/i18n/locale-switcher.tsx
  - apps/web/src/lib/i18n/domain-content.ts
  - apps/web/middleware.ts
  - apps/web/tests/i18n.test.tsx
---

## §1 - Description (BCP-14 normative)

This task builds the internationalization foundation for the frontend: next-intl wired into the TASK-WEB-001 shell, with Vietnamese as the default locale and English as the second, and - the defining decision - a hard split between two translation planes. UI labels (the app chrome: buttons, field labels, nav, empty states, error strings) live in message catalogs the frontend owns; domain content (pattern names, interpretation text, recommendations, classical excerpts and their three text layers) is served already translated by the backend (KB/RAG) and is never translated in the UI. It owns the i18n plumbing, the catalogs, and the domain-content resolver; it is the foundation TASK-WEB-008 extends with Chinese and RTL-readiness.

The frontend SHALL configure next-intl with a locale set of `["vi", "en"]`, `vi` default, locale-prefixed routing, and a middleware that resolves the active locale. All UI chrome SHALL read from the message catalogs (`messages/vi.json`, `messages/en.json`) via next-intl; no UI string SHALL be hard-coded in a component. Domain content SHALL be fetched from the backend in the active locale (the KB three-layer store TASK-KB-003 and the RAG interpretation TASK-RAG-003 carry their own expert translations) and rendered as-is; the UI SHALL NOT pass a pattern name, an interpretation, a recommendation, or a classical excerpt through any client-side or machine-translation function. The original Han (chu Han) SHALL always be preserved and displayed regardless of the active locale (strategy 7, Claude-07 s4.3) - a locale switch changes the surrounding prose layer, never the Han source text. A missing UI message key SHALL fall back to the `vi` value (and be flagged in dev), never render a raw key.

## §2 - Why this design (rationale for humans)

The product's cultural-respect guardrail (strategy 7, Claude-07 s4.3) is not a nicety bolted onto i18n - it is the reason the two planes must be split. A classical term like 青龍返首 or a passage from Yen Ba Dieu Tau Ca carries meaning that a generic machine translation flattens or fabricates; the same passage rendered by an expert translator into the three-layer form (Han / bach thoai / dich) is the honest artifact the product cites (TASK-KB-003). If the UI ran interpretation text or a pattern name through a translation API, it would silently manufacture unattributed, possibly wrong domain claims - exactly the fabrication the whole citation discipline exists to prevent (strategy 4.4). So domain content is translated once, by people, upstream, and the UI only ever displays it.

Keeping UI labels in catalogs and domain content on the backend also draws the maintenance line where it belongs: the frontend owns the words it invents (its own chrome), and the knowledge base owns the words it inherits (the tradition's text). That division lets English ship for the chrome long before every classical passage has an expert English rendering, without ever machine-translating the gap. Preserving the Han in every locale is the same respect-the-source rule seen from the interface: a user in any language can reach the original text, which is both an accuracy guarantee and a cultural one. This split is the foundation TASK-WEB-008 extends to Chinese precisely because Chinese is the source script, where the distinction matters most.

## §3 - Contract (config / catalogs / resolver)

### next-intl config (`i18n/routing.ts`, `i18n/request.ts`, `middleware.ts`)

```ts
// routing.ts
export const routing = defineRouting({
  locales: ["vi", "en"],     // TASK-WEB-008 adds "zh"
  defaultLocale: "vi",
  localePrefix: "as-needed"
});
```

The middleware resolves the active locale (path prefix, then `Accept-Language`, then default `vi`) and sets it on the request; `request.ts` loads the matching message catalog. The active locale is hosted in the TASK-WEB-001 shell's locale slot.

### The two planes

| Plane | Source | Translated by | Rendered |
|---|---|---|---|
| UI labels / chrome | `messages/{locale}.json` | the frontend (this task) | via next-intl `t("...")` |
| domain content (pattern names, interpretation, recommendations, classical excerpts, Han/bach thoai/dich) | backend KB (TASK-KB-003) + RAG (TASK-RAG-003) | domain experts, upstream | displayed as-is, never re-translated |

### Domain-content resolver (`lib/i18n/domain-content.ts`)

```ts
// requests domain content in the active locale; the backend returns the expert translation.
// NEVER machine-translates; NEVER strips the Han.
async function getDomainContent(kind: "pattern" | "interpretation" | "excerpt", ref: string, locale: "vi" | "en"): Promise<DomainText>;
type DomainText = { han?: string; text: string; locale: string; source?: string };   // han is always kept
```

The resolver requests the active-locale rendering from the backend and returns it verbatim; if the backend has no rendering for the active locale it returns the `vi` (or Han-plus-`vi`) form rather than a machine translation, and the caller displays that with the Han intact.

## §4 - Acceptance criteria

1. next-intl is configured with locales `["vi", "en"]`, default `vi`, locale-prefixed routing, and a middleware that resolves the active locale; the locale plugs into the TASK-WEB-001 shell.
2. Every UI chrome string is read from `messages/{locale}.json` via next-intl; a component with a hard-coded UI string fails a lint/test audit.
3. Switching locale changes the UI chrome (labels, nav, errors) and the surrounding prose layer of domain content, but never re-translates a pattern name, interpretation, recommendation, or classical excerpt in the client, and never strips or alters the Han.
4. Domain content is fetched in the active locale from the backend (TASK-KB-003 / TASK-RAG-003) and rendered as-is; the resolver has no machine-translation path (asserted - there is no translate call).
5. The original Han is displayed in every locale for any domain term that has one.
6. A missing UI message key falls back to the `vi` value (flagged in dev), never renders a raw key.

## §5 - Verification

- `tests/i18n.test.tsx`: asserts the locale set and default; renders the shell in `vi` and `en` and asserts the chrome comes from the catalogs; asserts a locale switch does not change (does not re-translate) a domain pattern name / interpretation fixture and keeps the Han; asserts the resolver returns backend text verbatim and has no translate path (a spy asserts no translation client is called); asserts a missing key falls back to `vi`.
- Audit: a token-style audit fails on a hard-coded UI string in a component (all chrome via next-intl).
- Accessibility: `lang` attribute reflects the active locale; the stacked-diacritics clip test (TASK-WEB-001) passes in `vi` and over Han-bearing domain terms in both locales.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build`.

## §6 - Implementation skeleton

1. `i18n/routing.ts` + `i18n/request.ts` + `middleware.ts`: next-intl with `["vi","en"]`, default `vi`, locale resolution; host the locale in the TASK-WEB-001 shell slot.
2. `messages/vi.json` + `messages/en.json`: the UI chrome catalogs (buttons, field labels, nav, empty states, error strings from the TASK-API-001 envelope mapping, the TASK-LEGAL-001 disclaimer keys).
3. `lib/i18n/domain-content.ts`: the resolver that fetches active-locale domain content from TASK-KB-003 / TASK-RAG-003 and returns it verbatim, Han preserved, with no translate path.
4. `components/i18n/locale-switcher.tsx`: the vi/en switch (Ochre focus ring, TASK-WEB-001).
5. Migrate the existing chrome (TASK-WEB-001/002/003) to `t("...")` keys; keep domain content on the resolver.
6. `tests/i18n.test.tsx` + the hard-coded-string audit.

## §7 - Dependencies

Depends on TASK-WEB-001 (the shell hosts the locale, and the components whose chrome moves into the catalogs). Reads domain content from TASK-KB-003 (the classical three-layer store, with expert translations) and TASK-RAG-003 (the interpretation text and recommendations in the requested locale). Provides the label i18n TASK-WEB-002 and TASK-WEB-003 consume for their chrome, and the disclaimer keys for TASK-LEGAL-001. Blocks TASK-WEB-008 (Chinese + RTL-ready extends this foundation). The split - frontend owns chrome, backend owns domain content - is the technical form of the cultural-respect guardrail (strategy 7).

## §8 - Example payloads

```json
// messages/en.json (UI chrome only - never domain content)
{ "cast": { "button": "Cast a chart", "datetime": "Date and time", "place": "Place" },
  "results": { "beginner": "Beginner", "expert": "Expert", "recommendations": "Recommendations" },
  "errors": { "FORBIDDEN_TIER": "This is a Premium capability." } }
```

```ts
// domain content is fetched, never translated in the UI; the Han is always kept
const p = await getDomainContent("pattern", "qimen_thanh_long_hoi_dau", "en");
// -> { han: "青龍返首", text: "Green Dragon Returns... (expert rendering, from TASK-KB-003)", locale: "en", source: "Yen Ba Dieu Tau Ca" }
// if no "en" expert rendering exists: -> { han: "青龍返首", text: "<vi rendering>", locale: "vi", source: "..." }  (NOT machine-translated)
```

## §9 - Open questions

- Server components vs client for locale: next-intl supports both. Default: resolve the locale in the middleware and load messages server-side, with a small client `locale-switcher`; keeps the catalogs off the client bundle where possible.
- What happens when the backend lacks an active-locale rendering for a domain term. Default: fall back to the `vi` rendering with the Han intact and flag it, never machine-translate; an English chrome around a Vietnamese-plus-Han passage is acceptable, a fabricated English classical term is not.
- Whether numbers/dates are localized. Default: localize UI-facing dates/numbers via next-intl formatters, but never localize a `datetime` that is an astronomical input (the cast uses explicit ISO + tz, TASK-WEB-002) - display formatting only, never the input value.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Machine-translated classical term | UI runs a pattern name / excerpt through a translate API | forbidden; domain content is expert-translated upstream and displayed as-is; the resolver has no translate path |
| Han stripped | a locale switch drops the chu Han | forbidden; the Han is preserved in every locale (strategy 7) |
| Hard-coded UI string | a component ships a literal label | forbidden; all chrome via next-intl catalogs; an audit fails the build |
| Raw key rendered | a missing message key shows `cast.button` | fall back to the `vi` value (flagged in dev), never render the key |
| Input value localized | a localized formatter alters the cast `datetime` | forbidden; the astronomical input stays explicit ISO + tz; localize display only |
| Domain content in catalogs | interpretation text placed in `messages/*.json` | forbidden; catalogs hold chrome only; domain content stays on the backend resolver |

## §11 - Notes

This task is the i18n foundation and it encodes the cultural-respect guardrail as an architecture, not a policy: the frontend owns the words it invents (chrome, in next-intl catalogs, `vi` default plus `en`), and the knowledge base owns the words it inherits (pattern names, interpretation, classical text, translated once by experts and displayed verbatim, Han always preserved). The UI never machine-translates a classical term, and a locale switch never touches the Han source. Keep the two planes split, keep the resolver translate-free, and this foundation extends cleanly to Chinese and RTL-readiness in TASK-WEB-008.
