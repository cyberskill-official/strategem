# @cyberskill/design React components in Next 16 — local adapter + upstream asks

Status: workaround shipped (W6). Owner ask list for the design-system team below.

## The blocker

`@cyberskill/design@1.0.0` cannot be imported as JS in Next 16 / React 19:

- `node_modules/@cyberskill/design/_esm/cs.mjs` (the only JS export, `exports["."]`)
  is browser-only: it uses **top-level await** and script-injects **React 18.3.1
  UMD from unpkg** (`https://unpkg.com/react@18.3.1/umd/react.development.js`),
  then reads a `window.CyberSkillDesignSystem_*` global from `_ds_bundle.js`.
  This fails at build/SSR time and would conflict with the app's React 19.
- The package **does** ship the real component sources as plain JSX with
  `.d.ts` types under `node_modules/@cyberskill/design/components/`, but the
  `exports` map in its `package.json` blocks deep imports
  (`@cyberskill/design/components/*` → ERR_PACKAGE_PATH_NOT_EXPORTED).
- CSS is fine: `@cyberskill/design/styles.css` and `tokens/*` are exported and
  already adopted (W5).

## The workaround (this repo)

- `apps/web/src/ds/index.ts` — a `"use client"` shim that re-exports the
  shipped JSX component sources via **relative paths** (relative specifiers
  bypass the `exports` map): Button, AIDisclosureBadge, ChatMessage,
  CitationList, ConfidenceMeter, HumanReviewGate, PromptInput. Types come from
  the sibling `.d.ts` files. Nothing is vendored/copied.
- `apps/web/next.config.ts` — `transpilePackages: ["@cyberskill/design"]` so
  Turbopack applies the JSX transform to those files (node_modules is skipped
  by default; without it the build fails with `Expected ';', got '{'`).
- Adopted for real: `src/components/ui/button.tsx`,
  `src/components/domain/ai-disclosure-badge.tsx`,
  `src/components/domain/human-review-gate.tsx` now render the DS components,
  with product copy/i18n (vi/en/zh) passed in as props.
- Kept local (markup-parity wrappers, reasons in each file's doc comment):
  `chat-message.tsx`, `prompt-input.tsx` (DS versions can't carry
  `data-testid`/aria hooks that e2e relies on — no rest-prop spreading),
  `confidence-meter.tsx` (DS level words are vi/en only, no override → would
  regress zh).

## Upstream asks (what the DS package needs so the shim can be deleted)

1. **SSR-safe ESM entry**: `import React from "react"` instead of top-level
   await + unpkg UMD script injection; no `window`/`document` at module scope.
2. **React as a peerDependency** (`react >=18 <20`), not a pinned UMD 18.3.1.
3. **Export the component sources**: add
   `"./components/*": "./components/*"` (or a compiled `./react` subpath) to
   `exports` so consumers don't need relative-path shims, and pre-transpile to
   `.js` (or document that consumers must transpile `.jsx`).
4. **Component API gaps** found during adoption:
   - spread rest props onto the root element (needed for `data-testid`,
     `aria-*`) — Button does this; ChatMessage/CitationList/etc. do not;
   - PromptInput: `aria-label` on the textarea, disable field while `busy`,
     disable send on empty value;
   - ConfidenceMeter: allow overriding the level words (or accept arbitrary
     locales) — built-in strings are vi/en only, app also ships zh;
   - AIDisclosureBadge: the `Sources:` prefix is hardcoded English; panel
     lacks Escape-to-close / dialog semantics;
   - `.d.ts` files omit the supported `lang` prop.
