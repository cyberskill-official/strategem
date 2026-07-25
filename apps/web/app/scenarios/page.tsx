"use client";

import { useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase } from "../../src/lib/api/client";
import { authHeaders } from "../../src/lib/auth/session";

type ScenarioRow = {
  label: string;
  best_score: number;
  windows: { start: string; end: string; score: number }[];
};

export default function ScenariosPage() {
  const { t } = useLocale();
  const [aStart, setAStart] = useState("2004-01-01T08:00");
  const [aEnd, setAEnd] = useState("2004-01-01T12:00");
  const [bStart, setBStart] = useState("2004-01-01T14:00");
  const [bEnd, setBEnd] = useState("2004-01-01T18:00");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ranked, setRanked] = useState<string[]>([]);
  const [results, setResults] = useState<ScenarioRow[]>([]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase()}/api/v1/scenario/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          top_n: 3,
          scenarios: [
            {
              label: t("scenarios.labelA"),
              start: new Date(aStart).toISOString(),
              end: new Date(aEnd).toISOString(),
              granularity: "gio",
            },
            {
              label: t("scenarios.labelB"),
              start: new Date(bStart).toISOString(),
              end: new Date(bEnd).toISOString(),
              granularity: "gio",
            },
          ],
        }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body?.error?.message || t("scenarios.error"));
        return;
      }
      setRanked(body.ranked_labels || []);
      setResults(body.results || []);
    } catch {
      setError(t("scenarios.errorNetwork"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cs-page cs-reveal" data-testid="scenarios-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("scenarios.kicker")}</p>
        <h1>{t("scenarios.title")}</h1>
        <p className="cs-lead-short">{t("scenarios.subtitle")}</p>
      </header>

      <form className="cs-card" onSubmit={onSubmit} data-testid="scenarios-form">
        <div className="cs-grid-2" style={{ gap: "1.5rem" }}>
          <fieldset>
            <legend>{t("scenarios.labelA")}</legend>
            <label>
              <span className="cs-muted">{t("timing.start")}</span>
              <input type="datetime-local" value={aStart} onChange={(e) => setAStart(e.target.value)} required />
            </label>
            <label>
              <span className="cs-muted">{t("timing.end")}</span>
              <input type="datetime-local" value={aEnd} onChange={(e) => setAEnd(e.target.value)} required />
            </label>
          </fieldset>
          <fieldset>
            <legend>{t("scenarios.labelB")}</legend>
            <label>
              <span className="cs-muted">{t("timing.start")}</span>
              <input type="datetime-local" value={bStart} onChange={(e) => setBStart(e.target.value)} required />
            </label>
            <label>
              <span className="cs-muted">{t("timing.end")}</span>
              <input type="datetime-local" value={bEnd} onChange={(e) => setBEnd(e.target.value)} required />
            </label>
          </fieldset>
        </div>
        <p className="cs-muted" style={{ marginTop: "0.75rem", fontSize: "0.9rem" }}>
          {t("scenarios.disclaimer")}
        </p>
        <button type="submit" className="cs-link-btn cs-link-btn--primary" disabled={loading} data-testid="scenarios-submit">
          {loading ? t("scenarios.loading") : t("scenarios.submit")}
        </button>
      </form>

      {error && (
        <p className="cs-card" role="alert">
          {error}
        </p>
      )}

      {results.length > 0 && (
        <section className="cs-card" data-testid="scenarios-results" style={{ marginTop: "1.5rem" }}>
          <h2>{t("scenarios.results")}</h2>
          <p className="cs-muted">
            {t("scenarios.ranked")}: {ranked.join(" → ")}
          </p>
          <div className="cs-grid-2" style={{ gap: "1rem", marginTop: "1rem" }}>
            {results.map((r) => (
              <div key={r.label} className="cs-card" data-testid="scenario-column">
                <h3>{r.label}</h3>
                <p>
                  {t("timing.score")}: {Number(r.best_score).toFixed(2)}
                </p>
                <ul>
                  {(r.windows || []).slice(0, 3).map((w, i) => (
                    <li key={i}>
                      {w.start} → {w.end} ({Number(w.score).toFixed(2)})
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
