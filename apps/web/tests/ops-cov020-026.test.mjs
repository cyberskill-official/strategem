/**
 * COV-020..026 web/ops surface smoke.
 */
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const repo = join(root, "../..");
const pricing = readFileSync(join(root, "app/pricing/page.tsx"), "utf8");
const graph = readFileSync(join(root, "app/learn/graph/page.tsx"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(pricing, /single-rail-note|singleRail|premium-checkout/);
assert.match(pricing, /payments\/checkout/);
assert.match(graph, /graph-explorer-page/);
assert.match(graph, /knowledge\/graph\/neighbors/);
assert.equal(typeof vi["pricing.singleRail"], "string");
assert.ok(existsSync(join(repo, "scripts/smoke-staging.sh")));
assert.ok(existsSync(join(repo, "docs/deploy/staging-runbook.md")));
assert.ok(existsSync(join(repo, "playwright.config.ts")) || existsSync(join(root, "playwright.config.ts")));

console.log("ops-cov020-026.test.mjs ok");
