/**
 * W6 trust surface smoke — follow-up chat contract, counsel gate, a11y targets.
 */
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const repo = join(root, "../..");

const prompt = readFileSync(join(root, "src/components/domain/prompt-input.tsx"), "utf8");
const chat = readFileSync(join(root, "src/components/domain/chat-message.tsx"), "utf8");
const follow = readFileSync(join(root, "src/components/domain/follow-up-chat.tsx"), "utf8");
const counsel = readFileSync(
  join(root, "src/components/domain/counsel-review-banner.tsx"),
  "utf8",
);
const gate = readFileSync(join(root, "src/lib/legal/counsel-gate.ts"), "utf8");
const shell = readFileSync(join(root, "src/components/app-shell/app-shell.tsx"), "utf8");
const top = readFileSync(join(root, "src/components/app-shell/top-bar.tsx"), "utf8");
const css = readFileSync(join(root, "src/styles/globals.css"), "utf8");
const client = readFileSync(join(root, "src/lib/api/client.ts"), "utf8");
const statusPath = join(repo, "docs/legal/vn-legal-review/gate-status.json");
const vi = readFileSync(join(root, "src/messages/vi.json"), "utf8");

assert.match(prompt, /cs-prompt/);
assert.match(prompt, /cs-prompt__field/);
assert.match(chat, /cs-chat-msg/);
assert.match(follow, /followUp\(/);
assert.match(follow, /AIDisclosureBadge/);
assert.match(follow, /data-testid="follow-up-chat"/);
assert.match(client, /\/follow-up/);

assert.match(counsel, /counsel-review-gate/);
assert.match(gate, /counsel_review:\s*"pending"/);
assert.match(shell, /CounselReviewBanner/);
// gate-status.json ships in the LEGAL-004 PR; assert when present so web PR stays independent.
if (existsSync(statusPath)) {
  const status = readFileSync(statusPath, "utf8");
  assert.match(status, /"verdict":\s*"pending"/);
}
assert.match(vi, /"chat\.title"/);
assert.match(vi, /"legal\.counsel\.pending"/);

assert.match(top, /ArrowDown/);
assert.match(top, /Escape/);
assert.match(css, /min-height:\s*44px/);
assert.match(css, /cs-theme-toggle/);
assert.match(css, /focus-visible/);

// APCA body: DS primary umber on page cream is Lc≈99; assert token anchors remain.
const dsColors = readFileSync(
  join(root, "node_modules/@cyberskill/design/tokens/colors.css"),
  "utf8",
);
assert.match(dsColors, /--cs-color-text-primary:\s*#45210[Ee]/);
assert.match(dsColors, /--cs-color-text-muted:\s*#6[Ee]5[Aa]4[Cc]/);

console.log("w6 trust/a11y/counsel smoke ok");
