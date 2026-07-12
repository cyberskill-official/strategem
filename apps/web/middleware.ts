import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { defaultLocale, locales, type Locale } from "./src/i18n/routing";

/**
 * Locale resolution — Vietnamese-first product:
 * 1. Explicit cookie always wins
 * 2. Otherwise default to `vi` (do NOT auto-switch from Accept-Language)
 *    so English browsers don't silently flip the product language.
 */
function resolveLocale(req: NextRequest): Locale {
  const cookie = req.cookies.get("locale")?.value;
  if (cookie && (locales as readonly string[]).includes(cookie)) {
    return cookie as Locale;
  }
  return defaultLocale;
}

export function middleware(req: NextRequest) {
  const locale = resolveLocale(req);
  const res = NextResponse.next();
  res.headers.set("x-locale", locale);
  if (!req.cookies.get("locale")) {
    res.cookies.set("locale", locale, {
      path: "/",
      maxAge: 60 * 60 * 24 * 365,
      sameSite: "lax",
    });
  }
  return res;
}

export const config = {
  matcher: ["/((?!_next|favicon.ico|.*\\..*).*)"],
};
