---
id: FR-LEGAL-001
title: "In-product disclaimer + AI-disclosure copy + positioning language rules - heritage education and decision support, never fortune-telling; no medical/legal/financial advice under a divination guise; the copy deck the shell and the AIDisclosureBadge consume"
module: LEGAL
priority: MUST
status: done
phase: P0
slice: 1
lang: doc
effort_h: 6
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s4.1, strategy 7, strategy RISK-4]
related_frs: [FR-WEB-001, FR-WEB-002, FR-WEB-003, FR-RAG-003, FR-LEGAL-003, FR-LEGAL-004, FR-WEB-006]
depends_on: [FR-WEB-001]
blocks: [FR-LEGAL-004]
new_paths:
  - docs/legal/positioning-language-rules.md
  - docs/legal/copy-deck/disclaimer.md
  - docs/legal/copy-deck/ai-disclosure.md
  - docs/legal/copy-deck/copy-keys.yaml
  - docs/legal/lexicon-do-dont.md
  - docs/legal/tests/copy-policy.md
---

## §1 - Description (BCP-14 normative)

This FR defines the product's positioning language: the in-product disclaimer, the AI-disclosure copy, and the do/don't language rules that keep Tam Thuc Strategem on the heritage-education side of the line (strategy 7, Claude-07 s4.1). It is a document FR - it produces the copy deck and the rules, versioned and reviewable, that other FRs consume: FR-WEB-001's shell renders the disclaimer and its `AIDisclosureBadge` reads the AI-limits copy by key, FR-RAG-003 aligns its framing guard with these rules, and FR-LEGAL-004 gates the whole thing on counsel sign-off before launch.

The product SHALL be framed as heritage education and structured decision support, and SHALL NEVER be framed as fortune-telling or a prediction of certain future events (strategy 7). The disclaimer SHALL be in-product and visible at the point of use - on the query screen (FR-WEB-002) and the results screen (FR-WEB-003) - and SHALL NOT be buried in a terms-of-service page only. The product language, including every AI interpretation (FR-RAG-003), SHALL: avoid asserting certain future events; avoid giving medical, legal, or financial advice under a divination guise; and avoid inducing fear or dependency. The AI-disclosure copy SHALL state that an interpretation is AI-generated, grounded in cited classical sources, and is a decision-support reading rather than a certain prediction or professional advice; it SHALL be the text the `AIDisclosureBadge` popover shows (named by a copy key). The copy SHALL exist in Vietnamese and English (FR-WEB-006), Vietnamese-first.

This FR provides the words and the rules; it does NOT implement the components (FR-WEB-001) nor the runtime guardrails (FR-RAG-003, FR-LEGAL-003), and its named VN statutes and final wording require counsel review before launch (FR-LEGAL-004).

## §2 - Why this design (rationale for humans)

Positioning is product-defining here, not a footer (strategy 7). The same classical method, described two ways, is either heritage education or "superstition for profit" - and under VN law that distinction carries real exposure (RISK-4: Nghi dinh 38/2021/ND-CP, Dieu 320 Bo luat Hinh su). The copy is therefore a controlled artifact: a single deck, versioned and counsel-reviewable, so the words a user reads are deliberate and consistent, not improvised per screen. Putting the disclaimer in-product at the point of use, rather than only in terms, is the difference between framing the user's expectation as they form it and disclaiming after the fact where no one reads it.

Owning the AI-limits copy here, keyed so the `AIDisclosureBadge` reads it, means legal owns the words and the component owns the affordance - the badge never hard-codes legal language, and a wording change is a reviewed diff in one place, not a hunt through components. The do/don't lexicon exists because the risk is linguistic: "you will marry in spring" is a forbidden certain-future assertion, "the reading suggests a supportive window for such plans" is heritage-framed decision support. Encoding that as an explicit forbidden/preferred list lets the RAG framing guard (FR-RAG-003) and a copy-policy check test against it, turning a soft editorial intent into something checkable. Avoiding fear and dependency ("consult daily or misfortune follows") is both an ethical floor and the exact pattern that reads as exploitation.

## §3 - Contract (copy deck / rules / keys)

### In-product disclaimer (`copy-deck/disclaimer.md`, keyed in `copy-keys.yaml`)

Shown in the FR-WEB-001 shell slot and on the query/results screens. Intent (final wording pending FR-LEGAL-004 counsel review):

```
key: legal.disclaimer.in_product
vi: "Tam Thuc Strategem gioi thieu cac phuong phap Tam Thuc (Luc Nham / Ky Mon / Thai At)
     nhu mot di san van hoa va mot cong cu ho tro ra quyet dinh - khong phai boi toan hay
     du doan tuong lai chac chan. San pham khong dua ra loi khuyen y te, phap ly hoac tai chinh."
en: "Tam Thuc Strategem presents the classical Tam Thuc methods (LiuRen / QiMen / TaiYi) as
     cultural heritage and a decision-support lens - not fortune-telling or a prediction of a
     certain future. It does not provide medical, legal, or financial advice."
```

### AI-disclosure copy (`copy-deck/ai-disclosure.md`) - the AIDisclosureBadge popover text

The `AIDisclosureBadge` (FR-WEB-001) reads these by key (`limitsCopyId`). Intent:

```
key: ai.limits.heritage_decision_support
vi: "Phan luan giai nay do AI tao ra tu cac trich dan kinh dien duoc truy xuat va co dan nguon.
     Day la mot goc nhin ho tro ra quyet dinh, khong phai du doan chac chan, va khong phai loi
     khuyen y te / phap ly / tai chinh. Mo hinh: {model}. Nguon: {citations}."
en: "This interpretation is AI-generated from retrieved, cited classical passages. It is a
     decision-support reading, not a certain prediction, and not medical, legal, or financial
     advice. Model: {model}. Sources: {citations}."
```

`{model}` and `{citations}` are filled from the FR-RAG-003 `AIDisclosure` block at render.

### Positioning language rules (`lexicon-do-dont.md`)

| Do (heritage / decision support) | Don't (forbidden) |
|---|---|
| "the classical reading suggests ...", "as a lens for reflection", "a supportive/less-supportive window", "consider ...", "the heritage method emphasizes ..." | "you will ...", "is destined / guaranteed", "certainly / definitely happens" (asserting a certain future) |
| "for planning and reflection" | "cure", "diagnosis", "you have <condition>" (medical advice) |
| "as one input to your own decision" | "you should sue / sign / invest in ..." (legal/financial advice) |
| "a heritage practice to explore" | "consult daily or misfortune will follow", "only this can protect you" (fear / dependency) |

### Copy-key registry (`copy-keys.yaml`)

The machine-readable id -> {vi, en} map the frontend consumes. Keys used at P0: `legal.disclaimer.in_product`, `ai.limits.heritage_decision_support`. New user-facing legal copy SHALL be added here by key, never inlined in a component.

## §4 - Acceptance criteria

1. The copy deck exists with the in-product disclaimer and the AI-disclosure copy, each in Vietnamese and English, registered by key in `copy-keys.yaml`.
2. The disclaimer key is the one the FR-WEB-001 shell and FR-WEB-002/003 screens render at the point of use (not only in terms); the `ai.limits.*` key is the one the `AIDisclosureBadge` `limitsCopyId` resolves.
3. The positioning rules document exists with the do/don't lexicon covering the four forbidden categories: certain-future assertion, medical advice, legal/financial advice, and fear/dependency.
4. No user-facing legal copy is hard-coded in a component - every such string resolves through a key in `copy-keys.yaml` (a lint/audit asserts it).
5. The copy avoids the forbidden lexicon: a copy-policy check over the deck (and, per FR-RAG-003, over AI output) flags any certain-future / medical / legal-financial / fear-dependency phrasing.
6. The deck is marked as requiring counsel review before launch (FR-LEGAL-004), with the named VN statutes referenced as the review context.

## §5 - Verification

- `docs/legal/tests/copy-policy.md` defines a copy-policy check (a lint the frontend and FR-RAG-003 can run): scan a string set against the forbidden lexicon and fail on a match; run it over the copy deck and over a sample of AI outputs (aligned with the FR-RAG-003 framing guard and FR-LEGAL-003).
- Key-resolution check: every `limitsCopyId` / disclaimer key referenced by FR-WEB-001/002/003 resolves to a `copy-keys.yaml` entry in both vi and en; a missing key fails the web build.
- Placement check: the disclaimer renders on the query and results screens (asserted by the FR-WEB-002/003 tests), not only on a terms page.
- Review gate: the deck carries a `counsel_review: pending` marker until FR-LEGAL-004 records sign-off; launch is blocked while pending.

## §6 - Implementation skeleton

1. `positioning-language-rules.md`: the heritage-education framing and the four forbidden categories, citing strategy 7 and the VN statutes as review context.
2. `copy-deck/disclaimer.md` + `copy-deck/ai-disclosure.md`: the disclaimer and AI-limits copy, vi + en, Vietnamese-first.
3. `copy-keys.yaml`: the id -> {vi, en} registry; register the P0 keys.
4. `lexicon-do-dont.md`: the do/don't table for authors, FR-RAG-003, and FR-LEGAL-003.
5. `tests/copy-policy.md`: the forbidden-lexicon check spec and how the frontend / RAG run it.
6. Mark `counsel_review: pending`; hand the named-statute list to FR-LEGAL-004.

## §7 - Dependencies

Depends on FR-WEB-001 (the shell slot and the `AIDisclosureBadge` that render this copy). Blocks FR-LEGAL-004 (the counsel-review checklist and sign-off gate operate on this deck and its statute references). Consumed by FR-WEB-002 and FR-WEB-003 (the disclaimer at the point of use), FR-RAG-003 (its framing guard aligns with the do/don't lexicon so no interpretation gives a certain-future or medical/legal/financial verdict), FR-LEGAL-003 (ethical-AI and cultural-sensitivity guardrails extend these rules), and FR-WEB-006 (i18n serves the vi/en copy).

## §8 - Example payloads

```yaml
# copy-keys.yaml (excerpt) - what the frontend resolves
legal.disclaimer.in_product:
  vi: "Tam Thuc Strategem gioi thieu cac phuong phap Tam Thuc ... khong phai boi toan ..."
  en: "Tam Thuc Strategem presents the classical Tam Thuc methods ... not fortune-telling ..."
ai.limits.heritage_decision_support:
  vi: "Phan luan giai nay do AI tao ra tu cac trich dan kinh dien ... Mo hinh: {model}. Nguon: {citations}."
  en: "This interpretation is AI-generated from retrieved, cited classical passages ... Model: {model}. Sources: {citations}."
```

```tsx
// FR-WEB-001 AIDisclosureBadge consuming the key
<AIDisclosureBadge model={disclosure.model} citationSources={interpretation.citations}
  reviewStatus={disclosure.review_status} limitsCopyId="ai.limits.heritage_decision_support" />
```

## §9 - Open questions

- Final wording and the exact statute framing require Vietnamese counsel (FR-LEGAL-004); the strings here are the intent, marked `counsel_review: pending`. Default: ship the deck as reviewable copy, gate launch on sign-off; do not treat this FR's wording as legally final.
- How much of the disclaimer is always-on vs a first-run acknowledgement. Default: a persistent, low-friction in-product disclaimer at the point of use (query + results), plus a one-time framing on first run; avoid a modal wall that trains users to dismiss it.
- Whether the AI-limits copy should name the specific model version or a general "AI model" label. Default: name the model from the FR-RAG-003 `AIDisclosure` block for transparency, with a stable fallback label if the field is absent.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Fortune-telling framing | copy asserts a certain future | forbidden; heritage-education / decision-support framing only; the copy-policy check flags certain-future phrasing (strategy 7) |
| Buried disclaimer | disclaimer only in terms of service | forbidden; it renders in-product at the point of use (query + results) |
| Advice under divination | copy or AI output gives medical/legal/financial direction | forbidden; the lexicon and the FR-RAG-003 framing guard block it |
| Fear / dependency | copy induces reliance or dread | forbidden; the lexicon flags it; ethical floor (FR-LEGAL-003) |
| Hard-coded legal copy | a component inlines legal text | forbidden; all such copy resolves via `copy-keys.yaml`; a missing key fails the build |
| Unreviewed launch | shipping before counsel sign-off | blocked; `counsel_review: pending` until FR-LEGAL-004 records sign-off |

## §11 - Notes

Positioning is product-defining, not decoration: the same classical method framed as heritage education is lawful and respectful, framed as guaranteed prediction it is the RISK-4 exposure the whole legal posture exists to avoid (strategy 7). Keep the words in one versioned deck, keep the disclaimer in-product at the point of use, keep the AI-limits copy keyed so legal owns the language and the `AIDisclosureBadge` owns the affordance, and keep the do/don't lexicon explicit so the RAG framing guard (FR-RAG-003) and the copy-policy check can enforce it. The named VN statutes and the final wording are informational until Vietnamese counsel signs off (FR-LEGAL-004) - this FR is the reviewable input to that gate, not a substitute for it.
