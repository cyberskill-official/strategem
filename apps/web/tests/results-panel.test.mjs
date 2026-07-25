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
assert.match(panel, /results-story-summary/);
assert.match(panel, /results\.storyTitle/);
assert.match(panel, /composeStorySummary|results-story-narrative/);
assert.match(panel, /toggle-board|chartToggle/);
assert.match(panel, /results\.disclaimer\.mid|disclaimer\.mid/);
assert.match(panel, /tech-details|techDetails/);
// WEB-012 / WEB-021 — next-step upsell + engine mode trust surface
assert.match(panel, /NextStepCard|next-step-card|results-next-step/);
assert.match(panel, /engine_mode|results\.engine/);

const nextStep = readFileSync(
  join(root, "src/components/results/next-step-card.tsx"),
  "utf8",
);
assert.match(nextStep, /data-testid="results-next-step"/);
assert.match(nextStep, /share-insight|navigator\.share/);
assert.match(nextStep, /\/pricing/);

assert.match(interp, /AIDisclosureBadge/);
assert.match(interp, /HumanReviewGate/);
assert.match(interp, /PersonaToggle/);
assert.match(interp, /requires_human_review/);

assert.match(panel, /FollowUpChat|follow-up-chat/);
assert.match(
  readFileSync(join(root, "src/components/domain/follow-up-chat.tsx"), "utf8"),
  /cs-prompt|PromptInput/,
);
assert.match(
  readFileSync(join(root, "src/components/domain/prompt-input.tsx"), "utf8"),
  /cs-prompt/,
);
assert.match(
  readFileSync(join(root, "src/components/domain/chat-message.tsx"), "utf8"),
  /cs-chat-msg/,
);

assert.match(patterns, /polarity-badge/);
assert.match(patterns, /aria-label=\{`\$\{t\("polarity\.label"\)\}|polarity\.(cat|hung|trung)/);
assert.match(patterns, /polarity\.cat|polarity\.hung|icon/);

assert.match(cite, /cite-han/);
assert.match(cite, /cite-bach/);
assert.match(cite, /cite-dich/);
assert.match(cite, /cite-locator/);

assert.match(page, /ResultsPanel/);
assert.match(page, /queryId|getQuery/);
assert.match(page, /getQuery/);
assert.doesNotMatch(page, /demoResponse|Demo fixture/);

console.log("results-panel tests ok");

