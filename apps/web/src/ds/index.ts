"use client";

/**
 * @cyberskill/design@1.0.0 — SSR-safe React adapter for Next 16 / React 19.
 *
 * Why this shim exists: the package's only JS entry (`_esm/cs.mjs`) is
 * browser-only — it uses top-level await and script-injects React 18.3.1 UMD
 * from unpkg — so `import "@cyberskill/design"` cannot work in Next (SSR or
 * client bundle). The package DOES ship the real component sources as plain
 * JSX under `components/`, but its `exports` map does not expose them as deep
 * imports (`@cyberskill/design/components/*` is blocked).
 *
 * Workaround: relative-path imports bypass the `exports` map entirely, so we
 * re-export the shipped JSX sources here. Turbopack transpiles the `.jsx`
 * files and follows the pnpm symlink; the sibling `.d.ts` files provide the
 * types. Every DS component uses hooks or event handlers, hence the single
 * "use client" boundary on this module.
 *
 * Language: DS components with built-in copy (HumanReviewGate, ConfidenceMeter,
 * PromptInput) resolve vi/en from the nearest `[lang]` ancestor or
 * `<html lang>`, which our LocaleProvider keeps in sync. They have no strings
 * for `zh` (falls back to en) — see the doc below before adopting one on a
 * zh-visible surface.
 *
 * Upstream asks are tracked in docs/design-system/react-adapter-next.md.
 * If upstream ever publishes a proper `exports["./components/*"]` entry, this
 * file collapses to plain package imports.
 */

export {
  Button,
  type ButtonProps,
} from "../../node_modules/@cyberskill/design/components/button/Button.jsx";
export {
  AIDisclosureBadge,
  type AIDisclosureBadgeProps,
} from "../../node_modules/@cyberskill/design/components/ai/AIDisclosureBadge.jsx";
export {
  ChatMessage,
  type ChatMessageProps,
} from "../../node_modules/@cyberskill/design/components/ai/ChatMessage.jsx";
export {
  CitationList,
  type Citation,
  type CitationListProps,
} from "../../node_modules/@cyberskill/design/components/ai/CitationList.jsx";
export {
  ConfidenceMeter,
  type ConfidenceMeterProps,
} from "../../node_modules/@cyberskill/design/components/ai/ConfidenceMeter.jsx";
export {
  HumanReviewGate,
  type HumanReviewGateProps,
} from "../../node_modules/@cyberskill/design/components/ai/HumanReviewGate.jsx";
export {
  PromptInput,
  type PromptInputProps,
} from "../../node_modules/@cyberskill/design/components/ai/PromptInput.jsx";
