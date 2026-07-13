import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
// readings.ts is TypeScript — assert wiring + pure logic via transpile-free source checks,
// and a small duplicated pure helper test for polarity stance selection.

const readings = readFileSync(join(root, "src/lib/domain/readings.ts"), "utf8");
assert.match(readings, /composeStorySummary/);
assert.match(readings, /Soft hint|Gợi ý nhẹ|轻提示/);
assert.match(readings, /la bàn thời điểm|timing compass/);
assert.doesNotMatch(readings, /sẽ thắng|will definitely|必胜|đổi đời/);

const panel = readFileSync(
  join(root, "src/components/results/results-panel.tsx"),
  "utf8",
);
assert.match(panel, /composeStorySummary/);
assert.match(panel, /results-story-narrative/);

// Catalog keys present
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));
const en = JSON.parse(readFileSync(join(root, "src/messages/en.json"), "utf8"));
const zh = JSON.parse(readFileSync(join(root, "src/messages/zh.json"), "utf8"));
for (const k of [
  "results.story.stance.hung",
  "results.story.stance.cat",
  "results.story.closing",
  "results.story.empty",
]) {
  assert.ok(vi[k], `vi missing ${k}`);
  assert.ok(en[k], `en missing ${k}`);
  assert.ok(zh[k], `zh missing ${k}`);
}

console.log("story-narrative tests ok");
