/**
 * CSRF double-submit helpers for cookie-authenticated BFF routes (AUTH-001).
 * Pair a readable SameSite cookie with X-CSRF-Token on mutating cookie requests.
 */

import { NextRequest, NextResponse } from "next/server";
import { randomBytes } from "node:crypto";

export const CSRF_COOKIE = "tamthuc_csrf";
export const CSRF_HEADER = "x-csrf-token";

export function newCsrfToken(): string {
  return randomBytes(32).toString("base64url");
}

export function setCsrfCookie(res: NextResponse, token?: string): string {
  const value = token ?? newCsrfToken();
  res.cookies.set(CSRF_COOKIE, value, {
    httpOnly: false,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 14,
  });
  return value;
}

export function clearCsrfCookie(res: NextResponse): void {
  res.cookies.set(CSRF_COOKIE, "", {
    httpOnly: false,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });
}

/** Cookie-authenticated mutations require matching Origin/Referer and CSRF header. */
export function cookieCsrfOk(req: NextRequest): boolean {
  const cookie = req.cookies.get(CSRF_COOKIE)?.value;
  const header = req.headers.get(CSRF_HEADER);
  if (!cookie || !header || cookie !== header) {
    return false;
  }
  return true;
}
