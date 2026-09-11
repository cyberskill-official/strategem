import { NextRequest, NextResponse } from "next/server";

/**
 * AUTH-001: revoke refresh on API (best-effort) and clear httpOnly cookie.
 */
function serverApiBase(): string {
  return (
    process.env.API_URL ||
    process.env.API_INTERNAL_URL ||
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "");
}

export async function POST(req: NextRequest) {
  const refresh = req.cookies.get("tamthuc_refresh")?.value;
  if (refresh) {
    try {
      await fetch(`${serverApiBase()}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });
    } catch {
      // cookie clear still proceeds
    }
  }
  const out = NextResponse.json({ ok: true });
  out.cookies.set("tamthuc_refresh", "", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });
  return out;
}
