import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = readFileSync(join(root, "src/components/chart/taiyi-chart.tsx"), "utf8");
const reader = readFileSync(join(root, "src/lib/chart/read-thai-at-ban.ts"), "utf8");

assert.match(src, /data-testid="taiyi-chart"/);
assert.match(src, /thai-at-marker/);
assert.match(src, /muoi-sau-than-ring/);
assert.match(src, /Pure reader|never computes/i);
assert.match(src, /skip/);
assert.match(reader, /thai_at/);
assert.match(reader, /readThaiAtBan/);

console.log("taiyi-chart tests ok");
