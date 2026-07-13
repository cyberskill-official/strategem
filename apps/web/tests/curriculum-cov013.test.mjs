/**
 * COV-013: L1–L4 curriculum UI + local persistence keys + practice deep-links.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const curriculum = readFileSync(join(root, "src/lib/learn/curriculum.ts"), "utf8");
const page = readFileSync(join(root, "app/learn/page.tsx"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(curriculum, /id: "L1"/);
assert.match(curriculum, /id: "L2"/);
assert.match(curriculum, /id: "L3"/);
assert.match(curriculum, /id: "L4"/);
assert.match(curriculum, /progressionOk/);
assert.match(curriculum, /LEARNER_LEVEL_KEY/);
assert.match(curriculum, /practiceHref: "\/cast\?system=qimen"/);
assert.match(curriculum, /practiceHref: "\/cross-system"/);
assert.match(page, /data-testid="curriculum-levels"/);
assert.match(page, /practice-\$\{lv\.id\}/);
assert.match(page, /curriculum-\$\{lv\.id\}/);
assert.match(page, /href=\{lv\.practiceHref\}/);
assert.equal(typeof vi["learn.curriculumTitle"], "string");

console.log("curriculum-cov013.test.mjs ok");
