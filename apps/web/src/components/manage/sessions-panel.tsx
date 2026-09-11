"use client";

import { useCallback, useState } from "react";
import { apiBase } from "../../lib/api/client";
import { authHeaders, getAccessToken } from "../../lib/auth/session";
import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

type SessionRow = {
  id: string;
  created_at: number;
  last_seen_at: number;
  expires_at: number;
  label: string | null;
  current: boolean;
};

/**
 * AUTH-001: list / revoke refresh families via /auth/sessions*.
 * Loads on explicit user action (avoids setState-in-effect lint).
 */
export function SessionsPanel() {
  const { t } = useLocale();
  const [sessions, setSessions] = useState<SessionRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!getAccessToken()) {
      setSessions([]);
      setError(t("sessions.signInRequired"));
      return;
    }
    setError(null);
    setBusy("load");
    try {
      const res = await fetch(`${apiBase()}/auth/sessions`, {
        headers: { ...authHeaders() },
      });
      if (res.status === 401) {
        setSessions([]);
        setError(t("sessions.signInRequired"));
        return;
      }
      if (!res.ok) {
        setError(t("sessions.loadError"));
        return;
      }
      const data = (await res.json()) as { sessions?: SessionRow[] };
      setSessions(Array.isArray(data.sessions) ? data.sessions : []);
    } catch {
      setError(t("sessions.loadError"));
    } finally {
      setBusy(null);
    }
  }, [t]);

  async function revokeOne(id: string) {
    setBusy(id);
    setError(null);
    try {
      const res = await fetch(`${apiBase()}/auth/sessions/${id}/revoke`, {
        method: "POST",
        headers: { ...authHeaders() },
      });
      if (!res.ok) {
        setError(t("sessions.revokeError"));
        return;
      }
      await load();
    } catch {
      setError(t("sessions.revokeError"));
    } finally {
      setBusy(null);
    }
  }

  async function revokeAll() {
    setBusy("all");
    setError(null);
    try {
      const res = await fetch(`${apiBase()}/auth/sessions/revoke-all`, {
        method: "POST",
        headers: { ...authHeaders() },
      });
      if (!res.ok) {
        setError(t("sessions.revokeError"));
        return;
      }
      await load();
    } catch {
      setError(t("sessions.revokeError"));
    } finally {
      setBusy(null);
    }
  }

  const signedIn = Boolean(getAccessToken());

  return (
    <section className="cs-card" data-testid="sessions-panel">
      <header>
        <h2>{t("sessions.title")}</h2>
        <p className="cs-muted" style={{ maxWidth: "48ch" }}>
          {t("sessions.lead")}
        </p>
      </header>
      {!signedIn ? (
        <p className="cs-muted" data-testid="sessions-signed-out">
          {t("sessions.signInRequired")}
        </p>
      ) : (
        <div style={{ marginBottom: "0.75rem" }}>
          <Button
            type="button"
            variant="secondary"
            size="xs"
            disabled={busy === "load"}
            data-testid="sessions-refresh"
            onClick={() => void load()}
          >
            {t("sessions.refresh")}
          </Button>
        </div>
      )}
      {error ? (
        <p role="alert" data-testid="sessions-error">
          {error}
        </p>
      ) : null}
      {signedIn && sessions && sessions.length === 0 && !error ? (
        <p className="cs-muted" data-testid="sessions-empty">
          {t("sessions.empty")}
        </p>
      ) : null}
      {sessions && sessions.length > 0 ? (
        <ul data-testid="sessions-list" style={{ listStyle: "none", padding: 0 }}>
          {sessions.map((s) => (
            <li
              key={s.id}
              data-testid="session-row"
              style={{
                display: "flex",
                gap: "1rem",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0.75rem 0",
                borderBottom: "1px solid var(--cs-border, #ddd)",
              }}
            >
              <div>
                <div>
                  {s.label || t("sessions.device")}
                  {s.current ? (
                    <span className="cs-muted"> — {t("sessions.current")}</span>
                  ) : null}
                </div>
                <div className="cs-muted" style={{ fontSize: "0.875rem" }}>
                  {t("sessions.lastSeen")}:{" "}
                  {new Date(s.last_seen_at * 1000).toLocaleString()}
                </div>
              </div>
              {!s.current ? (
                <Button
                  type="button"
                  variant="secondary"
                  size="xs"
                  disabled={busy === s.id}
                  data-testid="session-revoke"
                  onClick={() => void revokeOne(s.id)}
                >
                  {t("sessions.revoke")}
                </Button>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
      {signedIn && sessions && sessions.length > 0 ? (
        <div style={{ marginTop: "1rem" }}>
          <Button
            type="button"
            variant="secondary"
            disabled={busy === "all"}
            data-testid="sessions-revoke-all"
            onClick={() => void revokeAll()}
          >
            {t("sessions.revokeAll")}
          </Button>
        </div>
      ) : null}
    </section>
  );
}
