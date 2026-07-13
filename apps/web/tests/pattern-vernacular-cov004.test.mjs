/**
 * COV-004: pattern list shows vernacular names first (not raw engine ids as primary).
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const glossary = readFileSync(join(root, "src/lib/domain/glossary.ts"), "utf8");
const list = readFileSync(join(root, "src/components/results/pattern-list.tsx"), "utf8");

assert.match(glossary, /青龍返首/);
assert.match(glossary, /Thanh Long Phản Thủ/);
assert.match(glossary, /飛鳥跌穴/);
assert.match(list, /displayPatternName/);
assert.match(list, /data-testid="pattern-list"/);
// Primary display uses mapped name; classical only as secondary when different
assert.match(list, /cs-pattern-classical/);

console.log("pattern-vernacular-cov004.test.mjs ok");
