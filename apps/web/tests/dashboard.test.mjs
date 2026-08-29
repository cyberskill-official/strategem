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
assert.match(quick, /cs-link-btn/);
assert.match(quick, /cast\.button|t\(["']cast\.button["']\)/);
assert.match(dash, /flow-entry-cards|FlowEntryCards/);
assert.match(dash, /recent-charts|RecentCharts/);
assert.doesNotMatch(dash, /setSource\("demo"\)/);
assert.doesNotMatch(dash, /dashboard\.demoHint/);

// Touch target: link-btn uses --cs-control-height-md (44px) in tokens/globals.
const tokens = readFileSync(join(root, "src/styles/tokens.css"), "utf8");
const globals = readFileSync(join(root, "src/styles/globals.css"), "utf8");
assert.match(tokens, /--cs-control-height-md:\s*44px/);
assert.match(globals, /\.cs-link-btn[\s\S]*min-height:\s*var\(--cs-control-height-md\)/);

console.log("dashboard tests ok");
