"use client";

import { useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase } from "../../src/lib/api/client";
import { authHeaders, getAccessToken } from "../../src/lib/auth/session";

type SystemRead = {
  he: string;
  stance: string;
  scope: string;
  available: boolean;
  cat?: { name?: string }[];
  hung?: { name?: string }[];
  cast_ref?: string;
  reason?: string;
};

const HE_LABEL: Record<string, string> = {
  ky_mon: "Kỳ Môn",
  luc_nham: "Lục Nhâm",
  thai_at: "Thái Ất",
};

export default function CrossSystemPage() {
  const { t } = useLocale();
  const [datetime, setDatetime] = useState("2004-01-01T10:30");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reads, setReads] = useState<SystemRead[]>([]);
  const [summary, setSummary] = useState<string>("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (!getAccessToken()) {
        setError(t("cross.error"));
        return;
      }
      const res = await fetch(`${apiBase()}/api/v1/cross-system/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          datetime: new Date(datetime).toISOString(),
          tz: "+07:00",
          longitude: 106.7,
          systems: ["qimen", "liuren", "taiyi"],
          loai_cau_hoi: "trach_thoi",
        }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body?.error?.message || t("cross.error"));
        return;
      }
      setReads(body.reads || []);
      setSummary(body.agreement?.summary_vi || body.agreement?.summary || "");
    } catch {
      setError(t("cross.errorNetwork"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cs-page cs-reveal" data-testid="cross-system-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("cross.kicker")}</p>
        <h1>{t("cross.title")}</h1>
        <p className="cs-lead-short">{t("cross.subtitle")}</p>
      </header>

      <form className="cs-card" onSubmit={onSubmit} data-testid="cross-form">
        <label>
          <span className="cs-muted">{t("timing.start")}</span>
          <input
            type="datetime-local"
            value={datetime}
            onChange={(e) => setDatetime(e.target.value)}
            required
            data-testid="cross-datetime"
          />
        </label>
        <p className="cs-muted" style={{ fontSize: "0.9rem", marginTop: "0.75rem" }}>
          {t("cross.disclaimer")}
        </p>
        <button
          type="submit"
          className="cs-link-btn cs-link-btn--primary"
          disabled={loading}
          data-testid="cross-submit"
          style={{ marginTop: "1rem" }}
        >
          {loading ? t("cross.loading") : t("cross.submit")}
        </button>
      </form>

      {error && (
        <p className="cs-card" role="alert">
          {error}
        </p>
      )}

      {reads.length > 0 && (
        <section style={{ marginTop: "1.5rem" }} data-testid="cross-results">
          {summary ? (
            <p className="cs-card" data-testid="cross-consensus">
              {summary}
            </p>
          ) : null}
          <div className="cs-grid-3" style={{ gap: "1rem", marginTop: "1rem" }}>
            {reads.map((rd) => (
              <article key={rd.he} className="cs-card" data-testid="cross-column">
                <h3>{HE_LABEL[rd.he] || rd.he}</h3>
                {!rd.available ? (
                  <p className="cs-muted">{rd.reason || t("cross.unavailable")}</p>
                ) : (
                  <>
                    <p>
                      {t("cross.stance")}: <strong>{rd.stance}</strong>
                    </p>
                    <p className="cs-muted">
                      {t("cross.scope")}: {rd.scope}
                    </p>
                    <p className="cs-muted" style={{ fontSize: "0.8rem" }}>
                      ref: {rd.cast_ref || "—"}
                    </p>
                  </>
                )}
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
