/**
 * COV-014 practice · COV-015 library · COV-016 help/onboarding pages.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const practice = readFileSync(join(root, "app/practice/page.tsx"), "utf8");
const library = readFileSync(join(root, "app/library/page.tsx"), "utf8");
const help = readFileSync(join(root, "app/help/page.tsx"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(practice, /data-testid="practice-page"/);
assert.match(practice, /edu\/practice\/grade/);
assert.match(practice, /practice-cell-diffs|cell_diffs/);
assert.match(library, /data-testid="library-page"/);
assert.match(library, /library-layers/);
assert.match(library, /han/);
assert.match(help, /data-testid="help-page"/);
assert.match(help, /onboarding-panel/);
assert.match(help, /onboard-skip/);
assert.match(help, /onboard-reopen/);
assert.equal(typeof vi["practice.title"], "string");
assert.equal(typeof vi["help.title"], "string");

console.log("edu-cov014-016.test.mjs ok");
