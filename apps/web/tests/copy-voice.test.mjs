/**
 * VOICE.md denylist — first-screen keys must not contain prophecy / destiny spam.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

const FIRST_PREFIXES = [
  "home.",
  "cast.",
  "nav.",
  "sticky.",
  "results.story",
  "results.disclaimer",
  "pricing.lead",
  "pricing.free",
];

// Positive prophecy claims only (negations like "không hứa đổi đời" are OK).
const DENY = [
  /(?<!không hứa )đổi đời/i,
  /chắc chắn thắng/i,
  /xem mệnh/i,
  /sẽ sụp đổ/i,
  /định mệnh của bạn/i,
  /(?<!không phải lời )bói chắc/i,
  /will definitely win/i,
  /guaranteed fortune/i,
];

const keys = Object.keys(vi).filter((k) =>
  FIRST_PREFIXES.some((p) => k.startsWith(p)),
);
assert.ok(keys.length > 20, "expected first-screen keys");

const hits = [];
for (const k of keys) {
  const s = String(vi[k] ?? "");
  // Skip explicit anti-scam / disclaimer phrasing
  if (/không hứa|không phải|không thay|not a sure|not medical/i.test(s)) continue;
  for (const re of DENY) {
    if (re.test(s)) hits.push(`${k}: ${s.slice(0, 80)}`);
  }
}
assert.equal(hits.length, 0, `voice denylist hits:\n${hits.join("\n")}`);

// Preferred story title
assert.match(vi["results.storyTitle"] || "", /Tóm lại|short|短/i);
assert.ok(vi["results.disclaimer.mid"]);
assert.ok(vi["pricing.waitlistLocal"]);

console.log("copy-voice tests ok");
