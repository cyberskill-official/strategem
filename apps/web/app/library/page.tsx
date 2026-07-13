"use client";

/** COV-015 — classical library reader: Han + bạch thoại + dich. */

import { useCallback, useEffect, useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { apiBase } from "../../src/lib/api/client";

type Entry = {
  unit_id: string;
  title: string;
  han: string;
  bach_thoai: string;
  dich: string;
  layers?: { han?: string; bach_thoai?: string; dich?: string };
  system?: string;
};

export default function LibraryPage() {
  const { t } = useLocale();
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Entry[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.set("q", q.trim());
      const res = await fetch(`${apiBase()}/api/v1/edu/library?${params}`);
      const body = await res.json();
      if (!res.ok) {
        setError(t("library.error"));
        return;
      }
      setRows(body.entries || []);
    } catch {
      setError(t("library.errorNetwork"));
    }
  }, [q, t]);

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
    <div className="cs-page cs-reveal" data-testid="library-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("library.kicker")}</p>
        <h1>{t("library.title")}</h1>
        <p className="cs-lead-short">{t("library.subtitle")}</p>
      </header>

      <div className="cs-card">
        <label>
          <span className="cs-muted">{t("library.search")}</span>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            data-testid="library-search"
          />
        </label>
        <button
          type="button"
          className="cs-link-btn cs-link-btn--primary"
          onClick={() => void load()}
          style={{ marginTop: "0.75rem" }}
        >
          {t("library.refresh")}
        </button>
      </div>

      {error ? (
        <p role="alert" className="cs-card">
          {error}
        </p>
      ) : null}

      <ul style={{ listStyle: "none", padding: 0, marginTop: "1rem" }} data-testid="library-list">
        {rows.map((e) => (
          <li
            key={e.unit_id}
            className="cs-card"
            data-testid="library-entry"
            style={{ marginBottom: "0.75rem" }}
          >
            <h3 style={{ marginTop: 0 }}>{e.title}</h3>
            <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
              {e.system} · {e.unit_id}
            </p>
            <div
              data-testid="library-layers"
              style={{
                display: "grid",
                gap: "0.5rem",
                lineHeight: 1.7,
              }}
            >
              <p style={{ fontFamily: "serif", fontSize: "1.15rem", margin: 0 }}>
                <span className="cs-muted">{t("library.han")}: </span>
                {e.layers?.han || e.han || e.title}
              </p>
              <p style={{ margin: 0 }}>
                <span className="cs-muted">{t("library.bt")}: </span>
                {e.layers?.bach_thoai || e.bach_thoai || "—"}
              </p>
              <p style={{ margin: 0 }}>
                <span className="cs-muted">{t("library.dich")}: </span>
                {e.layers?.dich || e.dich || "—"}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
