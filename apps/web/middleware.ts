import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { defaultLocale, locales, type Locale } from "./src/i18n/routing";

function resolveLocale(req: NextRequest): Locale {
  const cookie = req.cookies.get("locale")?.value;
  if (cookie && (locales as readonly string[]).includes(cookie)) {
    return cookie as Locale;
  }
  const al = req.headers.get("accept-language") ?? "";
  if (al.toLowerCase().startsWith("en")) return "en";
  return defaultLocale;
}

export function middleware(req: NextRequest) {
  const locale = resolveLocale(req);
  const res = NextResponse.next();
  res.headers.set("x-locale", locale);
  if (!req.cookies.get("locale")) {
    res.cookies.set("locale", locale, { path: "/" });
  }
  return res;
}

export const config = {
  matcher: ["/((?!_next|favicon.ico|.*\\..*).*)"],
};
