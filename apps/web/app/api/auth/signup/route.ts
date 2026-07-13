import { NextRequest, NextResponse } from "next/server";

/**
 * COV-009: proxy register then login; set httpOnly refresh cookie.
 */
/** Server-only API origin. Do NOT use NEXT_PUBLIC_API_BASE (browser/host URL breaks inside Docker). */
function serverApiBase(): string {
  return (
    process.env.API_URL ||
    process.env.API_INTERNAL_URL ||
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "");
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const base = serverApiBase();

  const reg = await fetch(`${base}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const regData = await reg.json().catch(() => ({}));
  if (!reg.ok) {
    return NextResponse.json(regData, { status: reg.status });
  }

  const login = await fetch(`${base}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: body.email, password: body.password }),
  });
  const data = await login.json().catch(() => ({}));
  if (!login.ok) {
    return NextResponse.json(
      { registered: true, login_error: data },
      { status: login.status },
    );
  }
  const out = NextResponse.json({
    access: data.access,
    user_id: regData.user_id,
    email_verified: regData.email_verified,
  });
  if (data.refresh) {
    out.cookies.set("tamthuc_refresh", data.refresh, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 14,
    });
  }
  return out;
}
