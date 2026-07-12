import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const svg = readFileSync(join(root, "src/lib/chart/export-svg.ts"), "utf8");
const png = readFileSync(join(root, "src/lib/chart/export-png.ts"), "utf8");
const a11y = readFileSync(join(root, "src/lib/chart/a11y-labels.ts"), "utf8");
const print = readFileSync(join(root, "src/styles/chart-print.css"), "utf8");

assert.match(svg, /exportSvg/);
assert.match(png, /exportPng/);
assert.match(a11y, /palaceLabel/);
assert.match(a11y, /polarityLabel/);
assert.match(a11y, /diacriticSample/);
assert.match(print, /@media print/);
assert.match(print, /polarity-badge/);
assert.match(a11y, /huyền|ngã|nặng/);

console.log("chart-export tests ok");
