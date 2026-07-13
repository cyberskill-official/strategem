/**
 * COV-003: complete school-flag matrix (maoshan, zhong_gong_ky, dem_toan).
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const flags = readFileSync(join(root, "src/lib/flags/school-flags.ts"), "utf8");
const form = readFileSync(join(root, "src/components/manage/school-flags-form.tsx"), "utf8");
const results = readFileSync(join(root, "src/components/results/results-panel.tsx"), "utf8");
const glossary = readFileSync(join(root, "src/lib/domain/glossary.ts"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(flags, /maoshan/);
assert.match(flags, /zhong_gong_ky/);
assert.match(flags, /dem_toan/);
assert.match(flags, /toCastPayloadFlags/);
assert.match(form, /settings\.flag\./);
assert.match(form, /settings\.desc\./);
assert.match(results, /stamped-flags/);
assert.match(glossary, /maoshan/);
assert.match(glossary, /truoc_thai_at/);
// VI locale has human labels (not English-only chrome)
assert.match(vi["settings.flag.zhong_gong_ky"], /Trung|cung|Kỳ/i);
assert.match(vi["settings.flag.dem_toan"], /Đếm|toán/i);
assert.match(vi["settings.desc.dingju_method"], /Mao Sơn|sài bố/i);

console.log("school-flags-cov003.test.mjs ok");
