import { NextRequest, NextResponse } from "next/server";

/**
 * AUTH-001: rotate refresh via httpOnly cookie BFF.
 * Access token returned in JSON; new refresh stays in Secure HttpOnly cookie.
 */
function serverApiBase(): string {
  return (
    process.env.API_URL ||
    process.env.API_INTERNAL_URL ||
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "");
}

const COOKIE = "tamthuc_refresh";

export async function POST(req: NextRequest) {
  const cookieRefresh = req.cookies.get(COOKIE)?.value;
  let bodyRefresh: string | undefined;
  try {
    const body = await req.json();
    if (body && typeof body.refresh === "string") {
      bodyRefresh = body.refresh;
    }
  } catch {
    // cookie-only refresh is fine
  }
  const refresh = cookieRefresh || bodyRefresh;
  if (!refresh) {
    return NextResponse.json(
      { error: { code: "unauthorized", message: "authentication failed" } },
      { status: 401 },
    );
  }

  const base = serverApiBase();
  const res = await fetch(`${base}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const out = NextResponse.json(data, { status: res.status });
    if (res.status === 401) {
      out.cookies.set(COOKIE, "", {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        maxAge: 0,
      });
    }
    return out;
  }

  const out = NextResponse.json({
    access: data.access,
    token_type: data.token_type ?? "bearer",
  });
  if (data.refresh) {
    out.cookies.set(COOKIE, data.refresh, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 14,
    });
  }
  return out;
}
