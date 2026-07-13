/**
 * COV-017 palace sidebar, COV-018 input modes, COV-019 patterns page.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const sidebar = readFileSync(join(root, "src/components/chart/palace-detail-sidebar.tsx"), "utf8");
const results = readFileSync(join(root, "src/components/results/results-panel.tsx"), "utf8");
const form = readFileSync(join(root, "src/components/query/query-form.tsx"), "utf8");
const patterns = readFileSync(join(root, "app/patterns/page.tsx"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(sidebar, /data-testid="palace-detail-sidebar"/);
assert.match(sidebar, /aria-label/);
assert.match(results, /PalaceDetailSidebar/);
assert.match(results, /chart-with-sidebar/);
assert.match(form, /input-mode-field/);
assert.match(form, /calendar\/convert/);
assert.match(form, /never invent calendar math|convertViaCore|CORE/i);
assert.match(patterns, /data-testid="patterns-page"/);
assert.match(patterns, /knowledge\/patterns/);
assert.equal(typeof vi["cast.mode.lunar"], "string");
assert.equal(typeof vi["palace.sidebar"], "string");

console.log("palace-lunar-patterns-cov017-019.test.mjs ok");
