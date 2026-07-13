/**
 * COV-006: TaiYi story empty-state uses dedicated copy; glossary has TA patterns.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const readings = readFileSync(join(root, "src/lib/domain/readings.ts"), "utf8");
const glossary = readFileSync(join(root, "src/lib/domain/glossary.ts"), "utf8");

assert.match(readings, /systemKey === "taiyi"/);
assert.match(readings, /chủ–khách|host\/guest|主客/);
assert.match(glossary, /掩/);
assert.match(glossary, /擊/);

console.log("taiyi-story-cov006.test.mjs ok");
