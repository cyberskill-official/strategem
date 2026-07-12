"use client";

import { useEffect, useState } from "react";
import { useLocale } from "../../../src/components/i18n/locale-provider";
import { HistoryList } from "../../../src/components/manage/history-list";
import { getHistory, type ChartRef } from "../../../src/lib/api/history";

export default function ManageHistoryPage() {
  const { t } = useLocale();
  const [items, setItems] = useState<ChartRef[]>([]);
  const [source, setSource] = useState<"live" | "demo">("live");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await getHistory();
        if (!cancelled) {
          setItems(res.items);
          setSource(res.source);
        }
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : t("history.error"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [t]);

  return (
    <div className="cs-page cs-reveal">
      <header>
        <p className="cs-kicker">{t("nav.history")}</p>
        <h1>{t("history.title")}</h1>
        <p className="cs-muted" style={{ maxWidth: "48ch" }}>
          {t("history.lead")}
        </p>
      </header>
      {source === "demo" ? (
        <div className="cs-banner cs-banner--ochre" data-testid="history-demo-banner">
          {t("history.demoLoaded")}
        </div>
      ) : null}
      {loading ? <p data-testid="history-loading">{t("history.loading")}</p> : null}
      {error ? (
        <p data-testid="history-error" style={{ color: "var(--color-danger)" }}>
          {error}
        </p>
      ) : null}
      {!loading && !error && items.length === 0 ? (
        <div className="cs-empty" data-testid="history-empty">
          <div className="cs-empty__title">{t("history.title")}</div>
          <p style={{ margin: 0 }}>{t("history.empty")}</p>
        </div>
      ) : null}
      {!loading && items.length > 0 ? <HistoryList items={items} /> : null}
    </div>
  );
}
