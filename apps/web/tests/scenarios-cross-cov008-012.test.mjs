/**
 * COV-008 / COV-012 page presence + API path strings.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const scenarios = readFileSync(join(root, "app/scenarios/page.tsx"), "utf8");
const cross = readFileSync(join(root, "app/cross-system/page.tsx"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(scenarios, /data-testid="scenarios-page"/);
assert.match(scenarios, /\/api\/v1\/scenario\/compare/);
assert.match(cross, /data-testid="cross-system-page"/);
assert.match(cross, /\/api\/v1\/cross-system\/validate/);
assert.equal(typeof vi["nav.scenarios"], "string");
assert.equal(typeof vi["nav.cross"], "string");

console.log("scenarios-cross-cov008-012.test.mjs ok");
