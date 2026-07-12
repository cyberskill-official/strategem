"use client";

import { useLocale } from "../i18n/locale-provider";

export function RecommendationsList({ items }: { items: string[] }) {
  const { t } = useLocale();
  if (!items.length) return null;
  return (
    <section data-testid="recommendations-list" aria-label={t("report.recommendations")}>
      <h3>{t("report.recommendations")}</h3>
      <ul>
        {items.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
    </section>
  );
}
