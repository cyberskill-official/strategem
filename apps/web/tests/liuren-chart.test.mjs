import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = readFileSync(
  join(root, "src/components/chart/liuren-chart.tsx"),
  "utf8",
);
const reader = readFileSync(
  join(root, "src/lib/chart/read-luc-nham-ban.ts"),
  "utf8",
);

assert.match(src, /data-testid="liuren-chart"/);
assert.match(src, /ThienDiaBanView/);
assert.match(src, /TuKhoaView/);
assert.match(src, /TamTruyenView/);
assert.match(src, /ThienTuongRing/);
assert.match(src, /never re-computes|Pure reader/i);
assert.match(reader, /luc_nham/);
assert.match(reader, /readLucNhamBan/);

for (const f of [
  "thien-dia-ban.tsx",
  "tu-khoa.tsx",
  "tam-truyen.tsx",
  "thien-tuong-ring.tsx",
]) {
  const t = readFileSync(join(root, "src/components/chart", f), "utf8");
  assert.ok(t.length > 50, f);
}

console.log("liuren-chart tests ok");
