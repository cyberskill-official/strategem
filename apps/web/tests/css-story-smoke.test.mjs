/**
 * WEB-018 — CSS story/layout smoke.
 * Always checks source CSS. If `.next` exists (post-build), also checks compiled CSS.
 */
import assert from "node:assert/strict";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

/** Critical selectors that must ship — silent loss = “bugged UI”. */
export const REQUIRED_SELECTORS = [
  "cs-story-rail",
  "cs-story-step",
  "cs-visual-card",
  "cs-cta-band",
  "cs-faq-list",
  "cs-faq-item",
  "cs-hero-stage--story",
  "cs-chip",
  "cs-query-form",
  "cs-diff-band",
  "cs-story-summary",
  "cs-icon",
  "cs-sticky-cta",
];

function collectCssFiles(dir, acc = []) {
  if (!existsSync(dir)) return acc;
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) collectCssFiles(p, acc);
    else if (name.endsWith(".css")) acc.push(p);
  }
  return acc;
}

function assertSelectorsInText(label, text) {
  const missing = REQUIRED_SELECTORS.filter((s) => !text.includes(s));
  assert.equal(
    missing.length,
    0,
    `${label} missing CSS selectors: ${missing.join(", ")}`,
  );
}

// —— Source (always) ——
const wow = readFileSync(join(root, "src/styles/wow.css"), "utf8");
const globals = readFileSync(join(root, "src/styles/globals.css"), "utf8");
assertSelectorsInText("source wow.css+globals.css", wow + "\n" + globals);

// Import chain must load wow
assert.match(globals, /@import\s+["']\.\/wow\.css["']/);

// —— Built CSS (when present) ——
const nextDir = join(root, ".next");
if (existsSync(nextDir)) {
  const cssFiles = collectCssFiles(nextDir);
  assert.ok(cssFiles.length > 0, ".next exists but no CSS files found");
  const bundled = cssFiles.map((f) => readFileSync(f, "utf8")).join("\n");
  assertSelectorsInText("compiled .next CSS", bundled);
  console.log(`css-story-smoke: checked ${cssFiles.length} built CSS files`);
} else {
  console.log("css-story-smoke: source only (.next not present — skip build scan)");
}

console.log("css-story-smoke tests ok");
