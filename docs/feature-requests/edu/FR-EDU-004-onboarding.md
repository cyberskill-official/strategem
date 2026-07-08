---
id: FR-EDU-004
title: "Onboarding + help center - first-run guided tour that teaches the cast-read-decide loop and the meaning of the AIDisclosure and HumanReview components; a structured help-center of categories and articles, both content-as-data"
module: EDU
priority: COULD
status: ready_to_implement
phase: P3
slice: 1
lang: typescript
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.2, strategy 7, Grok-17, Grok-42, Claude-07 s2.2, Claude-07 s6]
related_frs: [FR-WEB-001, FR-LEGAL-001, FR-RAG-003, FR-RAG-004, FR-EDU-003, FR-WEB-006]
depends_on: [FR-WEB-001]
blocks: []
new_paths:
  - apps/web/src/content/edu/onboarding.ts
  - apps/web/src/content/edu/help.ts
  - apps/web/src/features/edu/onboarding/types.ts
  - apps/web/src/features/edu/onboarding/OnboardingFlow.tsx
  - apps/web/src/features/edu/help/HelpCenter.tsx
  - apps/web/src/features/edu/onboarding/onboarding.test.ts
---

## §1 - Description (BCP-14 normative)

This FR builds first-run onboarding and the help center: the surfaces that teach a new user how the product works and what its two AI-boundary components mean (Grok-17 onboarding, Grok-42 help center). It is a COULD-priority P3 polish item, but it carries a load-bearing responsibility - it is where the responsible-positioning of the product (strategy 7) is first taught to the user.

Onboarding SHALL be a first-run guided flow that teaches the cast-read-decide loop: cast a chart for a question, read the cited interpretation, and decide - the user always decides (Claude-07 s2.2 four-step framework, condensed; strategy 4.2 query flow surfaced to the user). It SHALL explain, in plain language, what the two components on the results surface mean: the AIDisclosureBadge (which parts are deterministic engine facts and which are cited AI interpretation, and on what sources - FR-RAG-003) and the HumanReviewGate (that important judgments pause for a human before reaching the user - FR-RAG-004). It SHALL frame the tool as a structured decision-analysis lens, not a fortune-telling verdict (strategy 7, Claude-07 s2.3), and SHALL run once per user (a completion flag), skippable and re-openable.

The help center SHALL be a structured catalog of `HelpArticle`s grouped into `HelpCategory`s, searchable, that a user can open from anywhere. Onboarding steps and help articles SHALL both be content-as-data (typed records with stable ids, like the FR-EDU-001 curriculum), so they are reviewable, translatable by id (FR-WEB-006), and rendered by a generic player rather than hardcoded. Both surfaces SHALL render in the FR-WEB-001 shell with Design System v1.3.0 components and no new tokens.

## §2 - Why this design (rationale for humans)

A new user meets a nine-cung chart and a wall of unfamiliar terms; without onboarding they will not know that the numbers are a deterministic cast and the prose is a cited interpretation they should weigh, not obey. Teaching the cast-read-decide loop up front is teaching the product's whole stance in three moves (Claude-07 s2.2): the chart gives a structured lens, the interpretation is grounded and cited, and the decision stays with the user. That is the four-step decision framework compressed to what a first-time user needs, and it is the honest framing the legal and cultural positioning requires (strategy 7).

The two AI components are not decoration and onboarding is where the user learns to read them (Claude-07 s5.3, s6). The AIDisclosureBadge makes the engine / AI boundary visible - here is a fact from the deterministic engine, here is an interpretation from the AI, and here are the sources it stands on. The HumanReviewGate makes the human-in-the-loop real - important judgments stop for a person before they reach the user. If a user does not understand these, the disclosures do their job on the interface but not in the user's head; a one-time guided explanation is cheap and closes that gap.

Making onboarding and help content-as-data, not hardcoded screens, is the same discipline as the curriculum (FR-EDU-001): a stable id per step and article means the copy is reviewable by non-engineers, translatable by id without re-authoring (FR-WEB-006), and playable by one generic component. It also keeps the responsible-positioning copy (FR-LEGAL-001) in one auditable place rather than scattered through JSX.

## §3 - Contract (content-as-data + players)

### Types (`apps/web/src/features/edu/onboarding/types.ts`)

```ts
// One step of the first-run tour. Content, keyed by a stable id (WEB-006 translates by id).
export interface OnboardingStep {
  id: string;              // stable, e.g. "onb.cast", "onb.read", "onb.decide", "onb.ai_disclosure", "onb.human_review"
  title: string;
  body: string;
  target?: OnboardingTarget;  // the surface this step highlights
  media?: string;          // optional illustration asset
}

// What a step points at - the three loop moves and the two AI components.
export type OnboardingTarget =
  | "cast" | "read" | "decide"
  | "ai_disclosure_badge" | "human_review_gate";

export interface OnboardingFlow {
  id: string;              // "first_run"
  steps: OnboardingStep[]; // ordered
  skippable: boolean;      // always true
}

export type HelpCategory =
  | "getting_started" | "casting" | "reading_interpretation"
  | "schools_and_flags" | "ai_and_review" | "account_and_data";

export interface HelpArticle {
  id: string;              // stable, e.g. "help.what_is_a_la_so"
  category: HelpCategory;
  title: string;
  body: string;            // markdown-ish content
  related: string[];       // other article ids
  seeAlso?: { id: string; work: string }[];  // optional deep-links into the FR-EDU-003 library
}

export interface HelpCenter {
  categories: HelpCategory[];
  articles: HelpArticle[];
}
```

### First-run content (`apps/web/src/content/edu/onboarding.ts`)

The first-run flow teaches the loop and the two components, in order:

```ts
export const firstRun: OnboardingFlow = {
  id: "first_run",
  skippable: true,
  steps: [
    { id: "onb.cast",   target: "cast",   title: "Cast a chart", body: "Enter a moment and a question; the engine casts one deterministic chart (la so)." },
    { id: "onb.read",   target: "read",   title: "Read the interpretation", body: "The reading is grounded in classical text and cited - a structured lens on the situation, not a verdict." },
    { id: "onb.decide", target: "decide", title: "You decide", body: "Weigh the chart against the real context and decide. The tool supports your thinking; it does not decide for you." },
    { id: "onb.ai_disclosure", target: "ai_disclosure_badge", title: "What the AI badge means",
      body: "The badge marks which parts are engine facts and which are AI interpretation, and on what sources. Tap it to see the model and citations." },
    { id: "onb.human_review", target: "human_review_gate", title: "What human review means",
      body: "Important judgments pause for a human reviewer before they reach you." },
  ],
};
```

### Help catalog (`apps/web/src/content/edu/help.ts`)

`HelpCenter` with the six categories above and their articles; the `ai_and_review` category explains the AIDisclosureBadge and HumanReviewGate in depth, and the `schools_and_flags` category explains why a chart stamps its school flags (strategy 4.4). Articles carry `related` ids and optional `seeAlso` links into the FR-EDU-003 library.

### Players (`OnboardingFlow.tsx`, `HelpCenter.tsx`)

```ts
// Generic tour player: renders steps in order, highlights each step's target, tracks completion.
export function useOnboarding(flow: OnboardingFlow): {
  step: OnboardingStep; index: number; next(): void; skip(): void; done: boolean;
};
// Completion is persisted per user so first-run shows once; re-openable from help.
export function hasCompletedOnboarding(userId: string): boolean;
```

`HelpCenter.tsx` renders the catalog: category nav, article view, and search over titles and bodies.

## §4 - Acceptance criteria

1. The `first_run` flow contains, in order, steps for the three loop moves (cast, read, decide) and for the two components (`ai_disclosure_badge`, `human_review_gate`); a test asserts all five targets are covered exactly once.
2. Onboarding runs once per user: after completion `hasCompletedOnboarding` is true and the flow does not re-trigger on next load; it remains skippable and re-openable from the help center.
3. The help center groups articles into the six `HelpCategory`s, renders an article with its `related` links, and supports search over title and body; the `ai_and_review` category has an article each for AIDisclosure and HumanReview.
4. Onboarding steps and help articles are content-as-data with stable ids, translatable by id (FR-WEB-006); no user-facing copy is hardcoded in the player components.
5. The positioning is responsible: the `decide` step states the user decides and the tool is a structured lens (strategy 7); a test asserts the first-run copy contains no fortune-telling / guaranteed-outcome phrasing (aligned with FR-LEGAL-001).
6. Both surfaces render in the FR-WEB-001 shell with DS v1.3.0 components and no new tokens.

## §5 - Verification

- Vitest (`onboarding.test.ts`): the `first_run` target-coverage test (five targets, once each, correct order); the run-once behavior via a stubbed completion store; the help catalog grouping and search; the content-as-data assertion (players take content, hold no copy).
- Positioning test: the first-run and the `ai_and_review` copy is checked against a disallowed-phrasing list (no "will happen", no "guaranteed", no destiny claims), sharing the FR-LEGAL-001 / FR-LEGAL-003 lexicon.
- i18n test: every `OnboardingStep` and `HelpArticle` has a stable id and resolves through the FR-WEB-006 label path for its chrome.
- Component/snapshot test: `OnboardingFlow` and `HelpCenter` render in the app shell with DS v1.3.0 only; the tour highlights the correct target element.
- Gates: `pnpm test`, `tsc --noEmit`, `eslint` (the WEB toolchain).

## §6 - Implementation skeleton

1. `types.ts`: `OnboardingStep`, `OnboardingTarget`, `OnboardingFlow`, `HelpCategory`, `HelpArticle`, `HelpCenter`.
2. `content/edu/onboarding.ts`: the `first_run` flow (the three loop moves + the two components).
3. `content/edu/help.ts`: the six-category catalog, with the `ai_and_review` and `schools_and_flags` articles.
4. `OnboardingFlow.tsx`: `useOnboarding`, the target-highlight, the completion persistence.
5. `HelpCenter.tsx`: category nav, article view with `related` and `seeAlso`, search.
6. `onboarding.test.ts`: target coverage, run-once, catalog, positioning, i18n.

## §7 - Dependencies

Depends on FR-WEB-001 (the app shell and Design System v1.3.0 components; onboarding highlights the AIDisclosureBadge and HumanReviewGate the shell defines). Explains the components owned by FR-RAG-003 (AIDisclosure) and FR-RAG-004 (HumanReviewGate), and shares its positioning lexicon with FR-LEGAL-001 (in-product disclaimer / positioning copy) and FR-LEGAL-003 (cultural-sensitivity language rules). Help articles deep-link into the FR-EDU-003 library. Translatable by id via FR-WEB-006.

## §8 - Example payloads

A help article in the `ai_and_review` category:

```ts
{
  id: "help.what_the_ai_badge_means",
  category: "ai_and_review",
  title: "What the AI disclosure badge means",
  body: "The chart itself is cast by a deterministic engine and is a fact. The interpretation beside it is written by an AI grounded in classical text; the badge tells you which is which, names the model, and lists the sources the reading cites. Open the badge to see them.",
  related: ["help.what_is_human_review", "help.why_charts_show_school_flags"],
  seeAlso: [{ id: "yba_thien_can_khac_ung_12", work: "Yen Ba Dieu Tau Ca" }],
}
```

## §9 - Open questions

- Guided-tour mechanism: a spotlight overlay on real elements, or a modal carousel? Default: a lightweight spotlight that highlights each step's `target` in the live results surface, falling back to a modal where no target is mounted yet (first run before the first cast).
- Depth of the help center at MVP: how many articles ship? Default: seed one article per loop move, one each for the two components, and one for school flags; grow the catalog from real support questions (Grok-42) rather than pre-writing exhaustively.
- Re-onboarding on major change: does a big UI change re-trigger the tour? Default: version the `first_run` flow id; a bumped version re-shows once, otherwise it stays completed.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Loop not taught | onboarding skips read or decide | target-coverage test fails; cast, read, decide must all appear |
| Components unexplained | no step for the badge or the gate | coverage test fails; both AI components have a step |
| Fortune-telling drift | copy promises a certain outcome | positioning test fails against the disallowed-phrasing list (strategy 7, FR-LEGAL-001) |
| Hardcoded copy | text baked into the player JSX | content-as-data test fails; players take content by id |
| Re-triggers every load | completion not persisted | run-once test fails; first run shows exactly once per user |
| New design token | onboarding / help adds a token | snapshot/lint asserts DS v1.3.0 tokens only |

## §11 - Notes

This is a small P3 polish FR with an outsized positioning job: it is where a new user first learns the cast-read-decide loop and what the AIDisclosureBadge and HumanReviewGate mean (Grok-17, Grok-42; Claude-07 s2.2, s6). Teaching that loop up front is teaching the product's whole responsible stance in three moves - a structured lens, a cited reading, and a decision that stays with the user (strategy 7). Keep onboarding and help as content-as-data with stable ids so the copy is reviewable, translatable by id (FR-WEB-006), and played by one generic component - the same discipline as the FR-EDU-001 curriculum. Language is TypeScript (DEC-2), rendering in the WEB-001 shell with no new tokens. refs Grok-17, Grok-42.
