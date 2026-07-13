/**
 * COV-005: LN chart surfaces khoa_the + vernacular glossary entries.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const chart = readFileSync(join(root, "src/components/chart/liuren-chart.tsx"), "utf8");
const glossary = readFileSync(join(root, "src/lib/domain/glossary.ts"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(chart, /data-testid="liuren-khoa-the"/);
assert.match(chart, /ban\.khoa_the/);
assert.match(glossary, /元首/);
assert.match(glossary, /重審/);
assert.equal(typeof vi["chart.liuren.khoaThe"], "string");

console.log("liuren-khoa-the-cov005.test.mjs ok");
