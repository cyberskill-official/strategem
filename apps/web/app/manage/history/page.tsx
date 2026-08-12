"use client";

import { useEffect, useState } from "react";
import { useLocale } from "../../../src/components/i18n/locale-provider";
import { HistoryList } from "../../../src/components/manage/history-list";
import {
  getHistory,
  type ChartRef,
  type HistorySource,
} from "../../../src/lib/api/history";

export default function ManageHistoryPage() {
  const { t } = useLocale();
  const [items, setItems] = useState<ChartRef[]>([]);
  const [source, setSource] = useState<HistorySource | "loading">("loading");
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
          if (res.source === "unavailable") {
            setError(t("history.unavailable"));
          } else if (res.source === "unauthorized") {
            setError(t("history.unauthorized"));
          }
        }
      } catch (e) {
        if (!cancelled) {
          setSource("unavailable");
          setError(e instanceof Error ? e.message : t("history.error"));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [t]);

  const showEmpty =
    !loading && !error && source === "empty" && items.length === 0;

  return (
    <div className="cs-page cs-reveal">
      <header>
        <p className="cs-kicker">{t("nav.history")}</p>
        <h1>{t("history.title")}</h1>
        <p className="cs-muted" style={{ maxWidth: "48ch" }}>
          {t("history.lead")}
        </p>
      </header>
      {loading ? <p data-testid="history-loading">{t("history.loading")}</p> : null}
      {error ? (
        <p data-testid="history-error" style={{ color: "var(--color-danger)" }}>
          {error}
        </p>
      ) : null}
      {showEmpty ? (
        <div className="cs-empty" data-testid="history-empty">
          <div className="cs-empty__title">{t("history.title")}</div>
          <p style={{ margin: 0 }}>{t("history.empty")}</p>
        </div>
      ) : null}
      {!loading && items.length > 0 ? <HistoryList items={items} /> : null}
    </div>
  );
}
