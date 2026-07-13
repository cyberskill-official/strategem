/**
 * COV-009 session helpers.
 * Refresh token prefers httpOnly cookie set by /api/auth/* route handlers.
 * Access token held in sessionStorage for Bearer API calls (short-lived).
 */

const ACCESS_KEY = "tamthuc_access";
const USER_KEY = "tamthuc_user";

export type SessionUser = {
  user_id?: string;
  email?: string;
  tier?: string;
};

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(ACCESS_KEY);
}

export function setAccessToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) sessionStorage.setItem(ACCESS_KEY, token);
  else sessionStorage.removeItem(ACCESS_KEY);
}

export function getSessionUser(): SessionUser | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionUser;
  } catch {
    return null;
  }
}

export function setSessionUser(user: SessionUser | null): void {
  if (typeof window === "undefined") return;
  if (user) sessionStorage.setItem(USER_KEY, JSON.stringify(user));
  else sessionStorage.removeItem(USER_KEY);
}

export function clearSession(): void {
  setAccessToken(null);
  setSessionUser(null);
}

export function authHeaders(): Record<string, string> {
  const t = getAccessToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}
