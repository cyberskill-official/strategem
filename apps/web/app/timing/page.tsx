"use client";

import { useMemo, useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase } from "../../src/lib/api/client";
import { authHeaders, getAccessToken } from "../../src/lib/auth/session";

type WindowRow = {
  start: string;
  end: string;
  score: number;
  cast_ref?: string;
  reasons?: string[];
  cat?: { name?: string; id?: string }[];
  hung?: { name?: string; id?: string }[];
};

type OptimizeResponse = {
  windows: WindowRow[];
  disclaimer?: string;
  ai_disclosure?: { used_llm?: boolean; mode?: string };
  error?: { code?: string; message?: string };
};

const QUESTION_TYPES = [
  { id: "trach_thoi", labelKey: "timing.q.trach_thoi" },
  { id: "cong_viec", labelKey: "timing.q.cong_viec" },
  { id: "gap_go", labelKey: "timing.q.gap_go" },
] as const;

function defaultRange() {
  const start = new Date("2004-01-01T08:00:00");
  const end = new Date("2004-01-01T20:00:00");
  const toLocal = (d: Date) => {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };
  return { start: toLocal(start), end: toLocal(end) };
}

export default function TimingPage() {
  const { t } = useLocale();
  const defaults = useMemo(() => defaultRange(), []);
  const [start, setStart] = useState(defaults.start);
  const [end, setEnd] = useState(defaults.end);
  const [question, setQuestion] = useState<string>("trach_thoi");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<OptimizeResponse | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      if (!getAccessToken()) {
        setError(t("timing.error"));
        return;
      }
      const base = apiBase();
      const url = `${base}/api/v1/timing/optimize`;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify({
          start: new Date(start).toISOString(),
          end: new Date(end).toISOString(),
          granularity: "gio",
          loai_cau_hoi: question,
          tz: "+07:00",
          longitude: 106.7,
          top_n: 5,
        }),
      });
      const body = (await res.json()) as OptimizeResponse;
      if (!res.ok) {
        setError(body.error?.message || t("timing.error"));
        return;
      }
      setResult(body);
    } catch {
      setError(t("timing.errorNetwork"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cs-page cs-reveal" data-testid="timing-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("timing.kicker")}</p>
        <h1>{t("timing.title")}</h1>
        <p className="cs-lead-short">{t("timing.subtitle")}</p>
      </header>

      <form className="cs-card" onSubmit={onSubmit} data-testid="timing-form">
        <div className="cs-grid-2" style={{ gap: "1rem" }}>
          <label>
            <span className="cs-muted">{t("timing.start")}</span>
            <input
              type="datetime-local"
              value={start}
              onChange={(ev) => setStart(ev.target.value)}
              required
              data-testid="timing-start"
            />
          </label>
          <label>
            <span className="cs-muted">{t("timing.end")}</span>
            <input
              type="datetime-local"
              value={end}
              onChange={(ev) => setEnd(ev.target.value)}
              required
              data-testid="timing-end"
            />
          </label>
        </div>
        <label style={{ display: "block", marginTop: "1rem" }}>
          <span className="cs-muted">{t("timing.questionType")}</span>
          <select
            value={question}
            onChange={(ev) => setQuestion(ev.target.value)}
            data-testid="timing-question"
          >
            {QUESTION_TYPES.map((q) => (
              <option key={q.id} value={q.id}>
                {t(q.labelKey)}
              </option>
            ))}
          </select>
        </label>
        <p className="cs-muted" style={{ marginTop: "0.75rem", fontSize: "0.9rem" }}>
          {t("timing.disclaimer")}
        </p>
        <button
          type="submit"
          className="cs-link-btn cs-link-btn--primary"
          disabled={loading}
          data-testid="timing-submit"
          style={{ marginTop: "1rem" }}
        >
          {loading ? t("timing.loading") : t("timing.submit")}
        </button>
      </form>

      {error && (
        <p className="cs-card" role="alert" data-testid="timing-error">
          {error}
        </p>
      )}

      {result && (
        <section className="cs-card" data-testid="timing-results" style={{ marginTop: "1.5rem" }}>
          <h2>{t("timing.results")}</h2>
          <ol className="cs-stagger" style={{ paddingLeft: "1.25rem" }}>
            {(result.windows || []).map((w, i) => (
              <li key={`${w.start}-${i}`} data-testid="timing-window" style={{ marginBottom: "1rem" }}>
                <div style={{ fontWeight: 600 }}>
                  #{i + 1} · {t("timing.score")}: {Number(w.score).toFixed(2)}
                </div>
                <div className="cs-muted">
                  {w.start} → {w.end}
                </div>
                {(w.reasons || []).map((r) => (
                  <div key={r} style={{ fontSize: "0.95rem" }}>
                    {r}
                  </div>
                ))}
              </li>
            ))}
          </ol>
          <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
            {result.disclaimer || t("timing.disclaimer")}
          </p>
        </section>
      )}
    </div>
  );
}
