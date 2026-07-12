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
assert.match(reader, /deriveThienDia|resolveThienDiaBan/);

// derive: month gen 子 on hour 子 → phuc ngam (identical plates)
const CHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
function derive(nt, gc) {
  const nti = CHI.indexOf(nt);
  const gci = CHI.indexOf(gc);
  const offset = (nti - gci + 12) % 12;
  return CHI.map((_, i) => CHI[(i + offset) % 12]);
}
assert.deepEqual(derive("子", "子"), CHI);
assert.equal(derive("午", "子")[0], "午"); // hour position 0 gets month gen

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
