import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));
const en = JSON.parse(readFileSync(join(root, "src/messages/en.json"), "utf8"));
const zh = JSON.parse(readFileSync(join(root, "src/messages/zh.json"), "utf8"));

const keys = Object.keys(vi).sort();
assert.deepEqual(keys, Object.keys(en).sort(), "vi/en key parity");
assert.deepEqual(keys, Object.keys(zh).sort(), "vi/zh key parity");
assert.equal(vi["cast.button"] !== en["cast.button"], true);
assert.equal(zh["cast.button"] !== en["cast.button"], true);

const domain = readFileSync(join(root, "src/lib/i18n/domain-content.ts"), "utf8");
// no callable machine-translation API — only the policy comment may mention it
assert.doesNotMatch(domain, /\.translate\(|google\.translate|deepl|i18next\.t\(/i);
assert.match(domain, /han/);
assert.match(domain, /NEVER machine-translates/);

const routing = readFileSync(join(root, "src/i18n/routing.ts"), "utf8");
assert.match(routing, /"vi"/);
assert.match(routing, /"en"/);
assert.match(routing, /"zh"/);
assert.match(routing, /defaultLocale/);
assert.match(routing, /textDirection|rtlLocales/);

console.log("i18n tests ok");
