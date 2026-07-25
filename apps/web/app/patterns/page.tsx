"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase } from "../../src/lib/api/client";
import { displayPatternName } from "../../src/lib/domain/glossary";

type PatternRow = {
  id?: string;
  system?: string;
  he?: string;
  name?: string;
  name_han?: string;
  polarity?: string;
  meaning_modern?: string;
  citations?: unknown[];
};

export default function PatternsPage() {
  const { t, locale } = useLocale();
  const [he, setHe] = useState<string>("");
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<PatternRow[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (he) params.set("he", he);
      if (q.trim()) params.set("q", q.trim());
      params.set("limit", "200");
      const res = await fetch(`${apiBase()}/api/v1/knowledge/patterns?${params}`);
      const body = await res.json();
      if (!res.ok) {
        setError(t("patterns.error"));
        return;
      }
      setRows(body.patterns || []);
      setTotal(body.total ?? (body.patterns || []).length);
    } catch {
      setError(t("patterns.errorNetwork"));
    } finally {
      setLoading(false);
    }
  }, [he, q, t]);

  useEffect(() => {
    let cancelled = false;
    const t = window.setTimeout(() => {
      void (async () => {
        if (cancelled) return;
        await load();
      })();
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(t);
    };
  }, [load]);

  return (
    <div className="cs-page cs-reveal" data-testid="patterns-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("patterns.kicker")}</p>
        <h1>{t("patterns.title")}</h1>
        <p className="cs-lead-short">{t("patterns.subtitle")}</p>
      </header>

      <div className="cs-card" data-testid="patterns-filters">
        <label>
          <span className="cs-muted">{t("patterns.filterHe")}</span>
          <select value={he} onChange={(e) => setHe(e.target.value)} data-testid="patterns-he">
            <option value="">{t("patterns.all")}</option>
            <option value="qimen">Kỳ Môn</option>
            <option value="liuren">Lục Nhâm</option>
            <option value="taiyi">Thái Ất</option>
          </select>
        </label>
        <label style={{ display: "block", marginTop: "0.75rem" }}>
          <span className="cs-muted">{t("patterns.search")}</span>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            data-testid="patterns-search"
            placeholder={t("patterns.searchPh")}
          />
        </label>
        <button
          type="button"
          className="cs-link-btn cs-link-btn--primary"
          onClick={() => void load()}
          disabled={loading}
          style={{ marginTop: "0.75rem" }}
        >
          {loading ? t("patterns.loading") : t("patterns.refresh")}
        </button>
        <p className="cs-muted" style={{ marginTop: "0.5rem" }}>
          {t("patterns.count")}: {total}
        </p>
      </div>

      {error ? (
        <p className="cs-card" role="alert">
          {error}
        </p>
      ) : null}

      <ul data-testid="patterns-list" style={{ listStyle: "none", padding: 0, marginTop: "1rem" }}>
        {rows.map((r, i) => {
          const vernacular = displayPatternName(String(r.name_han || r.name || ""), locale);
          const han = r.name_han || r.name || "";
          const polarity = (r.polarity || "").toLowerCase();
          return (
            <li key={r.id ?? i} className="cs-card" data-testid="pattern-row" style={{ marginBottom: "0.75rem" }}>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
                <strong>
                  {vernacular}
                  {vernacular !== han && /[\u4e00-\u9fff]/.test(han) ? (
                    <span className="cs-muted cs-pattern-classical"> {han}</span>
                  ) : null}
                </strong>
                <span className="cs-badge cs-badge--trung">{r.system || r.he}</span>
                {polarity ? (
                  <span
                    className={`cs-badge ${
                      polarity === "hung"
                        ? "cs-badge--hung"
                        : polarity === "cat"
                          ? "cs-badge--cat"
                          : "cs-badge--trung"
                    }`}
                  >
                    {r.polarity}
                  </span>
                ) : null}
              </div>
              {r.meaning_modern ? (
                <p style={{ margin: "0.35rem 0 0" }}>{r.meaning_modern}</p>
              ) : null}
              {Array.isArray(r.citations) && r.citations.length > 0 ? (
                <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
                  {t("patterns.citations")}:{" "}
                  {r.citations
                    .map((c) => (typeof c === "string" ? c : JSON.stringify(c)))
                    .slice(0, 3)
                    .join(", ")}
                </p>
              ) : null}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
