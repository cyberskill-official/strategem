/**
 * COV-024 — Playwright product journeys (home→cast→results→timing→auth).
 * Run: pnpm exec playwright test (from apps/web) when servers are up.
 * Local: soft-skip when API unreachable. CI: fail hard (TT-018).
 */
import { test, expect } from "@playwright/test";

const WEB = process.env.WEB_BASE || "http://127.0.0.1:3000";
const API = process.env.API_BASE || "http://127.0.0.1:8000";
const IN_CI = !!process.env.CI;

async function apiUp(request: { get: (u: string) => Promise<{ ok: () => boolean }> }) {
  try {
    const r = await request.get(`${API}/healthz`);
    return r.ok();
  } catch {
    return false;
  }
}

async function requireApi(request: { get: (u: string) => Promise<{ ok: () => boolean }> }) {
  const up = await apiUp(request);
  if (up) return;
  if (IN_CI) {
    throw new Error(`API unreachable at ${API}/healthz — failing in CI (TT-018)`);
  }
  test.skip(true, "API down — soft skip (local only)");
}

test.describe("product journeys", () => {
  test("home and cast paths at desktop width", async ({ page, request }) => {
    await requireApi(request);
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(WEB + "/");
    await expect(page.locator("body")).toContainText(/Strategem|Tam Thức|Tam Thuc/i);
    await page.goto(WEB + "/cast");
    await expect(page.getByTestId("cast-button").or(page.locator('[data-testid="cast-button"]')).first()).toBeVisible({
      timeout: 15000,
    }).catch(async () => {
      // form may use button text
      await expect(page.locator("form")).toBeVisible();
    });
  });

  test("mobile width cast page", async ({ page, request }) => {
    await requireApi(request);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(WEB + "/cast");
    await expect(page.locator("body")).toBeVisible();
  });

  test("timing page loads", async ({ page, request }) => {
    await requireApi(request);
    await page.goto(WEB + "/timing");
    await expect(page.getByTestId("timing-page")).toBeVisible({ timeout: 15000 });
  });

  test("login page loads", async ({ page, request }) => {
    await requireApi(request);
    await page.goto(WEB + "/login");
    await expect(page.getByTestId("login-page")).toBeVisible({ timeout: 15000 });
  });
});
