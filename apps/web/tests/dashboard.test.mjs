import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dash = readFileSync(join(root, "src/components/dashboard/dashboard.tsx"), "utf8");
const quick = readFileSync(join(root, "src/components/dashboard/quick-cast.tsx"), "utf8");

assert.match(dash, /data-testid="dashboard"/);
assert.match(dash, /disclaimer/);
assert.match(dash, /useLocale/);
assert.match(quick, /height: 44/);
assert.match(quick, /cast\.button|t\(["']cast\.button["']\)/);
assert.match(dash, /flow-entry-cards|FlowEntryCards/);
assert.match(dash, /recent-charts|RecentCharts/);

console.log("dashboard tests ok");
