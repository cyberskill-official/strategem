import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
const root = join(dirname(fileURLToPath(import.meta.url)), "..");

// W5: @cyberskill/design is the token source of truth.
// 1 — layout imports the DS styles.css foundation
const layout = readFileSync(join(root, "app/layout.tsx"), "utf8");
if (!layout.includes('import "@cyberskill/design/styles.css"'))
  throw new Error("layout must import @cyberskill/design/styles.css");

// 2 — DS package carries the immutable anchors
const dsColors = readFileSync(
  join(root, "node_modules/@cyberskill/design/tokens/colors.css"),
  "utf8",
);
if (!/#45210e/i.test(dsColors)) throw new Error("DS missing umber anchor");
if (!/#f4ba17/i.test(dsColors)) throw new Error("DS missing ochre anchor");

// 3 — local tokens.css is an alias layer only: no drifted brand redefinitions
const css = readFileSync(join(root, "src/styles/tokens.css"), "utf8");
if (/--cs-color-brand-umber\s*:/.test(css))
  throw new Error("tokens.css must not redefine --cs-color-brand-umber (DS owns it)");
if (/--cs-color-brand-ochre\s*:/.test(css))
  throw new Error("tokens.css must not redefine --cs-color-brand-ochre (DS owns it)");
const aliases = [
  "--color-ochre",
  "--color-info",
  "--control-height-md",
  "--line-height-body",
  "--radius-full",
];
for (const n of aliases) if (!css.includes(n)) throw new Error("missing alias " + n);

// 4 — components ride the DS .cs-* class contract, no hardcoded brand hex
const button = readFileSync(join(root, "src/components/ui/button.tsx"), "utf8");
if (button.includes("#F4BA17") || button.includes("#f4ba17"))
  throw new Error("hardcoded ochre in button");
if (!button.includes("cs-button")) throw new Error("button must use DS cs-button class");
const badge = readFileSync(
  join(root, "src/components/domain/ai-disclosure-badge.tsx"),
  "utf8",
);
if (!badge.includes("cs-ai-disclosure"))
  throw new Error("badge must use DS cs-ai-disclosure class");
const gate = readFileSync(
  join(root, "src/components/domain/human-review-gate.tsx"),
  "utf8",
);
if (!gate.includes("cs-review-gate")) throw new Error("gate must use DS cs-review-gate class");
if (!gate.includes("aria-live")) throw new Error("live");
console.log("WEB-001 token/component checks OK (DS-adopted)");
