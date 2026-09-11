/**
 * Browser helpers to attach X-CSRF-Token from the readable double-submit cookie.
 */

import { CSRF_COOKIE, CSRF_HEADER } from "./csrf";

export function readCsrfCookie(): string | null {
  if (typeof document === "undefined") return null;
  const parts = document.cookie.split(";").map((p) => p.trim());
  for (const part of parts) {
    if (part.startsWith(`${CSRF_COOKIE}=`)) {
      return decodeURIComponent(part.slice(CSRF_COOKIE.length + 1));
    }
  }
  return null;
}

export function csrfHeaders(): Record<string, string> {
  const token = readCsrfCookie();
  return token ? { [CSRF_HEADER]: token } : {};
}
