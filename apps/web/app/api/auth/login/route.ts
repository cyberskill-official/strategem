import { NextRequest, NextResponse } from "next/server";

/**
 * COV-009: proxy login + set httpOnly refresh cookie.
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
  const res = await fetch(`${base}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }
  const out = NextResponse.json({
    access: data.access,
    token_type: data.token_type ?? "bearer",
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
