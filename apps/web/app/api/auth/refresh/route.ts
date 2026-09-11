import { NextRequest, NextResponse } from "next/server";
import { cookieCsrfOk, setCsrfCookie } from "../../../../src/lib/auth/csrf";

/**
 * AUTH-001: rotate refresh via httpOnly cookie BFF.
 * Access token returned in JSON; new refresh stays in Secure HttpOnly cookie.
 * Cookie-bearing requests require same-site Origin/Referer + double-submit CSRF.
 */
function serverApiBase(): string {
  return (
    process.env.API_URL ||
    process.env.API_INTERNAL_URL ||
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "");
}

const COOKIE = "tamthuc_refresh";

function allowedOrigins(req: NextRequest): Set<string> {
  const host = req.headers.get("host");
  const extras = [
    process.env.WEB_ORIGIN,
    process.env.NEXT_PUBLIC_SITE_URL,
    process.env.AUTH_CSRF_ORIGINS,
  ]
    .filter(Boolean)
    .flatMap((v) => String(v).split(","))
    .map((s) => s.trim().replace(/\/$/, ""))
    .filter(Boolean);
  const set = new Set<string>(extras);
  if (host) {
    set.add(`https://${host}`);
    set.add(`http://${host}`);
  }
  // Local / preview convenience
  set.add("http://127.0.0.1:3000");
  set.add("http://localhost:3000");
  set.add("http://127.0.0.1:13000");
  set.add("http://localhost:13000");
  return set;
}

function originAllowed(req: NextRequest): boolean {
  const allowed = allowedOrigins(req);
  const origin = req.headers.get("origin");
  if (origin) {
    return allowed.has(origin.replace(/\/$/, ""));
  }
  const referer = req.headers.get("referer");
  if (referer) {
    try {
      const u = new URL(referer);
      return allowed.has(u.origin);
    } catch {
      return false;
    }
  }
  // No Origin/Referer: allow only non-browser / same-origin tooling without cookies
  return false;
}

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

  // CSRF: cookie-authenticated refresh must present Origin/Referer + double-submit token.
  if (cookieRefresh) {
    if (!originAllowed(req)) {
      return NextResponse.json(
        { error: { code: "forbidden", message: "origin check failed" } },
        { status: 403 },
      );
    }
    if (!cookieCsrfOk(req)) {
      return NextResponse.json(
        { error: { code: "forbidden", message: "csrf check failed" } },
        { status: 403 },
      );
    }
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
  setCsrfCookie(out);
  return out;
}
