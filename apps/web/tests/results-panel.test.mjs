import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const panel = readFileSync(
  join(root, "src/components/results/results-panel.tsx"),
  "utf8",
);
const interp = readFileSync(
  join(root, "src/components/results/interpretation-view.tsx"),
  "utf8",
);
const patterns = readFileSync(
  join(root, "src/components/results/pattern-list.tsx"),
  "utf8",
);
const cite = readFileSync(
  join(root, "src/components/results/citation-card.tsx"),
  "utf8",
);
const page = readFileSync(
  join(root, "app/results/[queryId]/page.tsx"),
  "utf8",
);

assert.match(panel, /deterministic-region/);
assert.match(panel, /ai-region/);
assert.match(panel, /region-boundary/);
assert.match(panel, /QimenNinePalace/);
assert.match(panel, /read-only/i);
assert.doesNotMatch(panel, /\.ban\s*=/);

assert.match(interp, /AIDisclosureBadge/);
assert.match(interp, /HumanReviewGate/);
assert.match(interp, /PersonaToggle/);
assert.match(interp, /requires_human_review/);

assert.match(patterns, /polarity-badge/);
assert.match(patterns, /icon \+ text|aria-label=\{`Polarity/);
assert.match(patterns, /Cát|Hung/);

assert.match(cite, /cite-han/);
assert.match(cite, /cite-bach/);
assert.match(cite, /cite-dich/);
assert.match(cite, /cite-locator/);

assert.match(page, /ResultsPanel/);
assert.match(page, /queryId/);

console.log("results-panel tests ok");
