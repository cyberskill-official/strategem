---
id: FR-WEB-001
title: "Next.js app shell + CyberSkill Design System v1.3.0 tokens + component library (Button, AIDisclosureBadge, HumanReviewGate) with the Vietnamese stacked-diacritics clip test"
module: WEB
priority: MUST
status: reviewing
phase: P0
slice: 1
lang: typescript
effort_h: 18
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-07 s5, strategy 4.4, Grok-15]
related_frs: [FR-PLAT-001, FR-WEB-002, FR-WEB-003, FR-WEB-006, FR-CHART-001, FR-LEGAL-001, FR-RAG-003, FR-RAG-004]
depends_on: [FR-PLAT-001]
blocks: [FR-WEB-002, FR-WEB-003, FR-WEB-004, FR-WEB-006, FR-CHART-001, FR-LEGAL-001, FR-EDU-001, FR-EDU-004]
new_paths:
  - apps/web/src/app/layout.tsx
  - apps/web/src/styles/tokens.css
  - apps/web/src/styles/globals.css
  - apps/web/src/lib/tokens.ts
  - apps/web/src/components/app-shell/app-shell.tsx
  - apps/web/src/components/app-shell/top-bar.tsx
  - apps/web/src/components/ui/button.tsx
  - apps/web/src/components/domain/ai-disclosure-badge.tsx
  - apps/web/src/components/domain/human-review-gate.tsx
  - apps/web/src/components/domain/index.ts
  - apps/web/tests/diacritics-clip.test.tsx
  - apps/web/tests/components.test.tsx
  - docs/design/design-system-v1.3.0.md
---

## §1 - Description (BCP-14 normative)

This FR builds the frontend foundation: the Next.js app shell, the CyberSkill Design System v1.3.0 as design tokens, and the shared component library every screen composes from - including the two domain components that make the deterministic-engine || AI boundary visible in the interface (strategy 4.4): `AIDisclosureBadge` and `HumanReviewGate`. It owns the shell, the tokens, and the component library; it does NOT build the query or results screens (FR-WEB-002, FR-WEB-003) nor the chart (FR-CHART-001), which consume this library.

The design tokens SHALL be the single source of visual truth (`tokens.css` as CSS custom properties, mirrored typed in `lib/tokens.ts`), and every component SHALL read tokens, never hard-coded values. The token set SHALL be exactly:

- Anchor colors: Umber `#45210E` (ground) and Ochre `#F4BA17` (primary action, focus ring, brand accent). Ochre SHALL NOT be used to carry semantic meaning.
- Semantic colors: success `#2E7D52`, danger `#B23B3B`, info `#2C5F8A`. Information SHALL NEVER be encoded by color alone - every semantic signal SHALL pair color with an icon and text.
- Fonts: Be Vietnam Pro (body), JetBrains Mono (code).
- Radius: sm `4`, md `8`, lg `12`, xl `16`, full `9999` (px).
- Control height: xs `24` (never a primary control), sm `36`, md `44` (default) (px).
- Space scale: token steps `{0,1,2,3,4,5,6,8,10,12,16,20,24}` mapping to `0..96px` (the step times 4px).
- Elevation: `e1..e5`, warm-earth (Umber-tinted) shadows, anchored at e1 `0 1px 2px rgba(69,33,14,0.06)`.
- Density: `compact | cozy | comfortable`.
- Glass: opt-in `blur(24px) saturate(120%)`, which SHALL collapse to a solid surface on print.

The app SHALL be Vietnamese-first: it SHALL pass a stacked-diacritics clip test at `100% / 200% / 400%` zoom on both light and dark themes, proving no descender/diacritic (e.g. the doubled marks in "ệ", "ự", "ỹ") is clipped by line-height, control height, or overflow. The two domain components SHALL be implemented to the anatomy in section 3 and SHALL be accessible (focus-visible ring in Ochre, ARIA roles, screen-reader-announced state).

## §2 - Why this design (rationale for humans)

A design system as tokens, not as copied values, is what keeps a Vietnamese-first divination product coherent as it grows from one screen to a dozen. The two anchor colors carry the brand's warm-earth identity - Umber as ground, Ochre as the single call-to-action and focus color - and the rule that Ochre never carries semantic meaning is deliberate: if the brand action color also meant "success" or "warning", a user could not tell a primary button from a status. Semantic meaning lives in the three semantic colors, and never in color alone, because a red/green-only signal fails for color-blind users and in grayscale print; pairing every signal with an icon and text is an accessibility floor, not a decoration.

The stacked-diacritics clip test is a first-class acceptance criterion because Vietnamese is the primary language and its stacked tone-plus-vowel marks (two diacritics on one glyph) are the first thing a Latin-tuned line-height clips. Testing it at 200% and 400% zoom on both themes catches the clipping that only appears when a user with low vision enlarges the text - exactly the user the accessibility floor is for.

The `AIDisclosureBadge` and `HumanReviewGate` are in this foundational FR, not bolted on later, because they are the interface expression of the platform's core architectural boundary (strategy 4.4): the engine computes deterministic facts, the AI interprets them, and the user must always be able to see which is which and whether a human vetted it. The badge is a link to an explanation of the AI's limits and sources, not a passive label; the gate is where a human's approve/reject is captured and announced. Building them as reusable, accessible components here means every AI-bearing screen (FR-WEB-003, reports, learning) uses the same trustworthy affordance rather than reinventing it.

## §3 - Contract (tokens / shell / components)

### Design tokens (`tokens.css`, typed in `lib/tokens.ts`)

```css
:root {
  /* anchor */
  --color-umber:  #45210E;   /* ground */
  --color-ochre:  #F4BA17;   /* primary action, focus ring, brand accent - NEVER semantic */
  /* semantic (always paired with icon + text, never color alone) */
  --color-success: #2E7D52;
  --color-danger:  #B23B3B;
  --color-info:    #2C5F8A;
  /* radius (px) */
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px; --radius-full: 9999px;
  /* control height (px) - xs is never a primary control */
  --control-xs: 24px; --control-sm: 36px; --control-md: 44px;   /* md is the default */
  /* space scale: step * 4px; steps {0,1,2,3,4,5,6,8,10,12,16,20,24} -> 0..96px */
  --space-0:0; --space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px; --space-5:20px;
  --space-6:24px; --space-8:32px; --space-10:40px; --space-12:48px; --space-16:64px;
  --space-20:80px; --space-24:96px;
  /* elevation: warm-earth (Umber-tinted) ramp; e1 is the specified anchor */
  --elev-1: 0 1px 2px rgba(69,33,14,0.06);
  --elev-2: 0 2px 4px rgba(69,33,14,0.08);
  --elev-3: 0 4px 8px rgba(69,33,14,0.10);
  --elev-4: 0 8px 16px rgba(69,33,14,0.12);
  --elev-5: 0 16px 32px rgba(69,33,14,0.16);
  /* type */
  --font-body: "Be Vietnam Pro", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
}
```

Density (`compact | cozy | comfortable`) is a data attribute on the shell that scales the space and control-height tokens by a documented factor. Glass is an opt-in utility (`backdrop-filter: blur(24px) saturate(120%)`) with a `@media print` rule that collapses it to a solid surface.

### App shell (`app-shell.tsx`, `top-bar.tsx`)

The chart-casting layout is two columns: a left input panel and a right chart-plus-interpretation panel (FR-WEB-002/003 fill them). The top bar is Umber ground with the Ochre brand mark on the left and the system tabs (LiuRen / QiMen / TaiYi) as navigation. The shell hosts the theme (light/dark), the density attribute, and the locale (FR-WEB-006), and reserves a persistent slot for the in-product disclaimer copy (FR-LEGAL-001).

### Button (`button.tsx`)

| Variant | Fill | Height token | Rule |
|---|---|---|---|
| primary | Ochre `#F4BA17` on Umber text | md `44px` (default) | the single call-to-action per view |
| secondary | outline / Umber | sm `36px` or md `44px` | |
| ghost | transparent | sm `36px` | |

xs `24px` controls exist but SHALL NOT be primary. Focus-visible ring is Ochre; disabled and loading states are defined; hit target respects the control-height token.

### AIDisclosureBadge (`ai-disclosure-badge.tsx`)

Anatomy (Claude-07 s5): rendered in the info color `#2C5F8A`, fully round (`--radius-full`), with an info icon and short text (never color alone). It is a link/button - activating it opens a popover that names (a) the model used, (b) the interpretation limits (heritage education / decision support, not a certain future - copy from FR-LEGAL-001), and (c) the citation sources backing the interpretation. It is a link to explanation, not decoration.

```tsx
type AIDisclosureBadgeProps = {
  model: string;                 // e.g. "gpt-4o-mini" (from the RAG-003 AIDisclosure block)
  citationSources: CitationRef[];// the sources shown in the popover
  reviewStatus: "pending" | "not_required" | "approved" | "rejected";
  limitsCopyId: string;          // key into the FR-LEGAL-001 copy deck
};
```

The badge is mandatory on any surface carrying AI output; it reads the `AIDisclosure` block FR-RAG-003 produces and reflects `reviewStatus`.

### HumanReviewGate (`human-review-gate.tsx`)

Anatomy (Claude-07 s5, strategy 4.4): a gate shown when an interpretation is flagged for review. It uses the warning and danger `#B23B3B` semantic tokens (never the Ochre brand accent for meaning), shows a risk label (what is being vetted and why), and presents Approve / Reject actions. Its state (pending / approved / rejected) SHALL be announced to screen readers via an ARIA live region, and the actions SHALL be keyboard-operable.

```tsx
type HumanReviewGateProps = {
  riskLabel: string;             // human-readable reason this needs review
  status: "pending" | "approved" | "rejected";
  onApprove(): void;
  onReject(reason: string): void;
};
```

The gate is the UI half of FR-RAG-004's review pipeline; this FR ships the component and its accessibility contract, FR-RAG-004 wires the queue and audit behind it.

## §4 - Acceptance criteria

1. Every token in section 3 exists as a CSS custom property in `tokens.css` and is mirrored in `lib/tokens.ts`; no component contains a hard-coded color, radius, spacing, or shadow value (lint rule / test enforces it).
2. Ochre `#F4BA17` is used only for primary action, focus ring, and brand accent - a test/audit asserts it is never bound to a semantic (success/danger/info) role.
3. No semantic signal is color-only: `success`/`danger`/`info` usages each pair color with an icon and text (component tests assert the icon+text presence).
4. The stacked-diacritics clip test passes at 100% / 200% / 400% zoom on light and dark themes - no diacritic or descender is clipped by line-height, control height, or overflow.
5. `Button` renders primary in Ochre at md `44px` by default; xs `24px` is available but rejected/blocked for the primary variant.
6. `AIDisclosureBadge` renders in info `#2C5F8A`, fully round, opens a popover naming the model, the interpretation limits, and the citation sources, and reflects `reviewStatus`; it is focusable and operable by keyboard.
7. `HumanReviewGate` uses warning+danger tokens, shows a risk label and Approve/Reject, and announces its state to screen readers via an ARIA live region.

## §5 - Verification

- `tests/diacritics-clip.test.tsx`: renders a fixture of stacked-diacritic strings (e.g. "Nghiệp", "Tự", "Quỹ", full-tone vowels) inside buttons, tabs, inputs, and body text at 100/200/400% and on both themes; asserts computed line boxes contain the glyph ink boxes (no clip). This is the Vietnamese-first gate.
- `tests/components.test.tsx`: token-only styling (no literals) audit; Ochre-never-semantic audit; icon+text-for-every-semantic-signal audit; `Button` variant/height matrix; `AIDisclosureBadge` popover content (model + limits + sources) and keyboard operability; `HumanReviewGate` ARIA live announcement and keyboard actions.
- Accessibility: `jest-axe` (or equivalent) has zero violations on the shell, `Button`, `AIDisclosureBadge`, and `HumanReviewGate`; focus-visible ring is Ochre.
- Gates: `pnpm --filter web lint`, `pnpm --filter web test`, `next build` (FR-PLAT-001 web lane).

## §6 - Implementation skeleton

1. `tokens.css` + `lib/tokens.ts`: the full token set from section 3; wire fonts (Be Vietnam Pro, JetBrains Mono) and the Tailwind theme to read the tokens.
2. `app-shell.tsx` + `top-bar.tsx`: the two-column shell, the Umber top bar with the Ochre brand mark and the system tabs, theme + density + locale hosting, and the disclaimer slot (FR-LEGAL-001).
3. `button.tsx`: the variant/size matrix with the xs-never-primary rule and the Ochre focus ring.
4. `ai-disclosure-badge.tsx`: the info-color round badge + popover (model, limits copy, citation sources); read the FR-RAG-003 `AIDisclosure` shape.
5. `human-review-gate.tsx`: the warning+danger gate with risk label, approve/reject, and the ARIA live region.
6. `tests/diacritics-clip.test.tsx` and `tests/components.test.tsx`; author `docs/design/design-system-v1.3.0.md` as the human-readable token + component reference.

## §7 - Dependencies

Depends on FR-PLAT-001 (the `apps/web` scaffold, Tailwind, shadcn/ui). Blocks FR-WEB-002 (query input composes this library), FR-WEB-003 (results screen composes the chart + the two domain components), FR-WEB-004 (dashboard), FR-WEB-006 (i18n plugs into the shell's locale slot), FR-CHART-001 (the chart is rendered inside this shell and uses the tokens and the cat/hung icon+text convention), FR-LEGAL-001 (the disclaimer copy fills the shell slot and the badge popover), and the EDU learner surfaces. Reads the `AIDisclosure` contract from FR-RAG-003 and pairs with FR-RAG-004 behind `HumanReviewGate`.

## §8 - Example payloads

```tsx
// AIDisclosureBadge fed by the FR-RAG-003 AIDisclosure block
<AIDisclosureBadge
  model="gpt-4o-mini"
  citationSources={interpretation.citations}
  reviewStatus={interpretation.disclosure.review_status}   // "not_required"
  limitsCopyId="ai.limits.heritage_decision_support"       // FR-LEGAL-001 copy key
/>

// HumanReviewGate shown when interpretation.requires_human_review is true
<HumanReviewGate
  riskLabel="High-stakes question; interpretation pending expert review."
  status="pending"
  onApprove={approve}
  onReject={reject}
/>
```

## §9 - Open questions

- Storybook vs a lightweight component gallery for the library. Default: a minimal gallery route in `apps/web` at MVP so the components are viewable without a second toolchain; add Storybook only if the library outgrows it.
- Where the AIDisclosure "interpretation limits" copy lives. Default: the FR-LEGAL-001 copy deck keyed by id (`limitsCopyId`), so legal owns the words and the component owns the affordance - the badge never hard-codes legal language.
- Dark-theme semantic hues: whether `#2E7D52 / #B23B3B / #2C5F8A` need dark-mode adjusted variants for contrast. Default: define dark variants that preserve the same meaning and pass contrast, still paired with icon+text; keep the light values exact as specified.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Hard-coded value | a component uses a literal color/px | forbidden; token-only audit fails the build; components read `tokens.css` |
| Ochre carries meaning | Ochre used for success/warning/status | forbidden; the Ochre-never-semantic audit fails; semantic hues carry meaning, Ochre is action/brand only |
| Color-only signal | a status shown by color with no icon/text | forbidden; every semantic signal pairs color + icon + text; test asserts it |
| Diacritic clipped | line/control height clips stacked marks | the clip test fails at 100/200/400% on light+dark; fix line-height / control height before ship |
| Badge as decoration | AIDisclosureBadge does not open the explanation | forbidden; it is a link to model + limits + sources; a test asserts the popover content |
| Silent review state | HumanReviewGate state not announced | the ARIA live region announces pending/approved/rejected; axe + a screen-reader test assert it |

## §11 - Notes

This FR is the visual and trust foundation for the whole frontend, so two things must be exact: the tokens (values as specified - Umber `#45210E`, Ochre `#F4BA17`, the semantic trio, the radius/height/space/elevation scales) and the two domain components. `AIDisclosureBadge` and `HumanReviewGate` are not styling - they are the interface expression of the deterministic-engine || AI boundary (strategy 4.4), so treat their anatomy (badge = link to model/limits/sources; gate = warning+danger, risk label, approve/reject, screen-reader-announced) as contract, not suggestion. The Vietnamese-first clip test is a gate, not a nicety: a product whose primary language is Vietnamese must not clip a single stacked diacritic at any supported zoom.
