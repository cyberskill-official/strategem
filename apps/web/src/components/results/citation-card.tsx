"use client";

import { useLocale } from "../i18n/locale-provider";

export type CitationCardProps = {
  citationId?: string;
  han?: string;
  bachThoai?: string;
  dich?: string;
  locator?: string;
  source?: string;
};

export function CitationCard({
  citationId,
  han,
  bachThoai,
  dich,
  locator,
  source,
}: CitationCardProps) {
  const { t, locale } = useLocale();
  // Never mix: for vi/zh hide English dich if it looks like EN stub
  const showDich =
    dich &&
    (locale === "en" ||
      !/Retrieved classical|Educational|local \/ stub/i.test(dich));

  return (
    <article
      data-testid="citation-card"
      id={citationId ? `cite-${citationId}` : undefined}
      className="cs-card"
      style={{ padding: 14, marginBottom: 10 }}
    >
      {source ? (
        <div style={{ fontWeight: 650, marginBottom: 6 }}>{source}</div>
      ) : null}
      {han ? (
        <p data-testid="cite-han" style={{ fontFamily: "serif", fontSize: "1.1rem" }}>
          <strong>{t("chart.citationHan")}:</strong> {han}
        </p>
      ) : null}
      {bachThoai ? (
        <p data-testid="cite-bach">
          <strong>{t("chart.citationVernacular")}:</strong> {bachThoai}
        </p>
      ) : null}
      {showDich ? (
        <p data-testid="cite-dich">
          <strong>{t("chart.citationGloss")}:</strong> {dich}
        </p>
      ) : null}
      {locator ? (
        <p data-testid="cite-locator" className="cs-muted" style={{ marginBottom: 0 }}>
          {locator}
        </p>
      ) : null}
    </article>
  );
}
