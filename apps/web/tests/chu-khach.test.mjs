import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = readFileSync(
  join(root, "src/lib/strat/chuKhachFramework.ts"),
  "utf8",
);

assert.match(src, /DecisionFrame/);
assert.match(src, /step1_framing/);
assert.match(src, /step4_decision/);
assert.match(src, /competitor/);
assert.match(src, /you decide/i);
assert.match(src, /presentDecisionFrame/);
assert.match(src, /step3_context_prompts/);
assert.doesNotMatch(src, /you will win/);

console.log("chu-khach tests ok");
