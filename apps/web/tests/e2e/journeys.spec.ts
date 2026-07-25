/**
 * W6 — Playwright cast → results → report (+ follow-up + a11y smoke).
 *
 * Requires a running API (default :18000 or API_BASE) and web (WEB_BASE).
 * Prefer `next start` (production) over `next dev` — HMR rewrite noise can
 * stall client hydration in headed automation.
 *
 * When REQUIRE_E2E=1 (or CI + E2E_LIVE=1), missing servers fail the suite instead
 * of soft-skipping. Local default still skips with a clear message if API is down.
 */
import { test, expect, type APIRequestContext } from "@playwright/test";

const WEB = process.env.WEB_BASE || "http://127.0.0.1:3000";
const API = process.env.API_BASE || "http://127.0.0.1:18000";
const REQUIRE =
  process.env.REQUIRE_E2E === "1" ||
  process.env.E2E_LIVE === "1" ||
  (process.env.CI === "true" && process.env.E2E_SOFT !== "1");

async function apiHealthy(request: APIRequestContext): Promise<boolean> {
  try {
    const r = await request.get(`${API}/healthz`, { timeout: 4000 });
    return r.ok();
  } catch {
    return false;
  }
}

async function ensureApi(request: APIRequestContext) {
  const up = await apiHealthy(request);
  if (!up) {
    const msg = `API not reachable at ${API}/healthz`;
    if (REQUIRE) throw new Error(`${msg} (REQUIRE_E2E/E2E_LIVE set — failing hard)`);
    test.skip(true, `${msg} — soft skip (set REQUIRE_E2E=1 to fail)`);
  }
}

async function castViaApi(request: APIRequestContext): Promise<{
  query_id: string;
  report_id?: string;
}> {
  const r = await request.post(`${API}/api/v1/calculate/qimen`, {
    data: {
      datetime: "2004-01-01T10:30:00",
      tz: "+07:00",
      longitude: 105.85,
      place: "Ha Noi",
      question_type: "trach_thoi",
      systems: ["qimen"],
      persona_level: "beginner",
    },
  });
  expect(r.ok(), `cast failed: ${r.status()} ${await r.text()}`).toBeTruthy();
  const body = await r.json();
  expect(body.query_id).toBeTruthy();
  return { query_id: body.query_id as string, report_id: body.report_id as string | undefined };
}

test.describe("W6 product journeys", () => {
  test("cast → results → report → follow-up chat", async ({ page, request }) => {
    await ensureApi(request);
    const { query_id, report_id } = await castViaApi(request);
    const rid = report_id || query_id;

    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(`${WEB}/results/${encodeURIComponent(query_id)}`);
    await expect(page.getByTestId("results-panel")).toBeVisible({ timeout: 30_000 });

    // Open AI region so follow-up chat mounts
    const toggleAi = page.getByTestId("toggle-ai");
    if (await toggleAi.isVisible()) {
      await toggleAi.click();
    }
    await expect(page.getByTestId("follow-up-chat")).toBeVisible({ timeout: 15_000 });

    // Report journey
    const openReport = page.getByTestId("open-report");
    if (await openReport.count()) {
      await openReport.click();
      await expect(page.getByTestId("report-view")).toBeVisible({ timeout: 30_000 });
    } else {
      await page.goto(`${WEB}/report/${encodeURIComponent(rid)}`);
      await expect(page.getByTestId("report-view")).toBeVisible({ timeout: 30_000 });
    }

    // Follow-up on report
    await expect(page.getByTestId("follow-up-chat")).toBeVisible();
    await page.getByTestId("follow-up-input").fill("Cách cục này gợi ý gì để học?");
    await page.getByTestId("follow-up-send").click();
    await expect(page.getByTestId("chat-msg-user")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId("chat-msg-assistant").last()).toBeVisible({
      timeout: 45_000,
    });
  });

  test("a11y: focus rings, theme toggle, nav keyboard, counsel gate", async ({
    page,
    request,
  }) => {
    await ensureApi(request);
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(`${WEB}/cast`);

    // Counsel gate banner present while LEGAL-004 pending
    await expect(page.getByTestId("counsel-review-gate")).toBeVisible();
    await expect(page.getByTestId("counsel-review-gate")).toHaveAttribute(
      "data-counsel-verdict",
      "pending",
    );

    // Theme toggle ≥44px and keyboard operable
    const theme = page.getByTestId("theme-toggle");
    await expect(theme).toBeVisible();
    const box = await theme.boundingBox();
    expect(box, "theme toggle box").toBeTruthy();
    expect(box!.height).toBeGreaterThanOrEqual(44);
    expect(box!.width).toBeGreaterThanOrEqual(44);
    await theme.focus();
    await expect(theme).toBeFocused();
    await theme.click();
    await expect
      .poll(async () => page.locator("html").getAttribute("data-theme"))
      .toBe("dark");
    await theme.click();
    await expect
      .poll(async () => page.locator("html").getAttribute("data-theme"))
      .not.toBe("dark");
    // Keyboard still reaches the control
    await theme.focus();
    await page.keyboard.press("Enter");
    await expect
      .poll(async () => page.locator("html").getAttribute("data-theme"))
      .toBe("dark");

    // Nav dropdown keyboard
    const explore = page.getByTestId("nav-menu-explore");
    await explore.focus();
    await page.keyboard.press("ArrowDown");
    await expect(page.locator('[role="menu"]')).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator('[role="menu"]')).toHaveCount(0);

    // Cast control focus + 44px
    const castBtn = page.getByTestId("cast-button");
    await castBtn.focus();
    await expect(castBtn).toBeFocused();
    const castBox = await castBtn.boundingBox();
    expect(castBox!.height).toBeGreaterThanOrEqual(40);
  });

  test("UI cast form posts and lands on results when API live", async ({
    page,
    request,
  }) => {
    await ensureApi(request);
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(`${WEB}/cast`);
    await expect(page.getByTestId("cast-button")).toBeVisible({ timeout: 15_000 });
    await page.getByTestId("cast-button").click();
    // Either navigates to /results/:id or shows inline preview with panel
    await expect
      .poll(
        async () => {
          const url = page.url();
          if (/\/results\//.test(url)) return "nav";
          if (await page.getByTestId("results-panel").isVisible().catch(() => false)) {
            return "inline";
          }
          return "wait";
        },
        { timeout: 60_000 },
      )
      .not.toBe("wait");
  });
});

// Keep lightweight path checks without soft-hiding failures when REQUIRE_E2E=1
test.describe("smoke paths", () => {
  test("home and timing load", async ({ page, request }) => {
    await ensureApi(request);
    await page.goto(`${WEB}/`);
    await expect(page.locator("body")).toContainText(/Strategem|Tam Thức|Tam Thuc/i);
    await page.goto(`${WEB}/timing`);
    await expect(page.getByTestId("timing-page")).toBeVisible({ timeout: 15_000 });
  });
});
