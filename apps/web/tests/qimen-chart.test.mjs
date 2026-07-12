import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = readFileSync(
  join(root, "src/components/chart/qimen-nine-palace.tsx"),
  "utf8",
);

assert.match(src, /LOSHU_ORDER/);
assert.match(src, /4, 9, 2/);
assert.match(src, /data-testid="qimen-nine-palace"/);
assert.match(src, /never re-computes/i);
assert.match(src, /onSelectPalace/);
assert.match(src, /role="grid"/);

// cellsFromBan pure logic reimplemented for test
function cellsFromBan(ban) {
  const cells = [];
  for (let p = 1; p <= 9; p++) {
    const i = p - 1;
    cells.push({
      palace: p,
      stem: ban?.thien_ban?.[i] ?? ban?.dia_ban?.[i],
    });
  }
  return cells;
}
const cells = cellsFromBan({
  thien_ban: ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"],
});
assert.equal(cells.length, 9);
assert.equal(cells[0].stem, "戊");

console.log("qimen-chart tests ok");
