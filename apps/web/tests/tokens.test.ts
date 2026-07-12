import { readFileSync } from "node:fs";
import { join } from "node:path";
import { CSS_TOKEN_NAMES, tokens } from "../src/lib/tokens";

const root = join(__dirname, "..");

function assert(cond: unknown, msg: string): asserts cond {
  if (!cond) throw new Error(msg);
}

const css = readFileSync(join(root, "src/styles/tokens.css"), "utf8");
for (const name of CSS_TOKEN_NAMES) {
  assert(css.includes(name), `missing CSS token ${name}`);
}

assert(tokens.color.ochre.toUpperCase() === "#F4BA17", "ochre mismatch");
// Ochre only for brand/primary/focus — not semantic keys
const semantic = [tokens.color.success, tokens.color.danger, tokens.color.info];
assert(
  semantic.every((c) => c.toUpperCase() !== "#F4BA17"),
  "ochre must not bind to semantic roles",
);

// components use CSS vars not raw hex (except documentation tokens file)
const button = readFileSync(join(root, "src/components/ui/button.tsx"), "utf8");
assert(!button.includes("#F4BA17"), "button must use CSS vars");
assert(button.includes("var(--color-ochre)"), "primary uses ochre token");
assert(button.includes("var(--control-height-md)"), "md height token");

const badge = readFileSync(join(root, "src/components/domain/ai-disclosure-badge.tsx"), "utf8");
assert(badge.includes("var(--color-info)"), "badge uses info token");
assert(badge.includes("var(--radius-full)"), "badge fully round");
assert(badge.includes("aria-"), "badge a11y");

const gate = readFileSync(join(root, "src/components/domain/human-review-gate.tsx"), "utf8");
assert(gate.includes("var(--color-warning)"), "gate warning");
assert(gate.includes("aria-live"), "gate live region");
assert(gate.includes("Approve") && gate.includes("Reject"), "approve/reject");

// diacritics: line-height + overflow visible
const globals = readFileSync(join(root, "src/styles/globals.css"), "utf8");
assert(globals.includes("line-height: var(--line-height-body)"), "body line-height");
assert(globals.includes("overflow: visible"), "no clip");

console.log("WEB-001 token/component checks OK");
