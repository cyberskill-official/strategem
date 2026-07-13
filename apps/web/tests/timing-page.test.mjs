/**
 * COV-007: timing page module loads and exposes expected test ids in source.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const page = readFileSync(join(root, "app/timing/page.tsx"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(page, /data-testid="timing-page"/);
assert.match(page, /data-testid="timing-form"/);
assert.match(page, /\/api\/v1\/timing\/optimize/);
assert.match(page, /timing\.disclaimer/);
assert.equal(typeof vi["nav.timing"], "string");
assert.equal(typeof vi["timing.title"], "string");
assert.match(vi["timing.disclaimer"], /học hỏi|suy nghĩ/i);

console.log("timing-page.test.mjs ok");
