"use client";

import { useLocale } from "../i18n/locale-provider";
import { displayPatternName } from "../../lib/domain/glossary";

export type CitationCardProps = {
  citationId?: string;
  han?: string;
  bachThoai?: string;
  dich?: string;
  locator?: string;
  source?: string;
};

/** Vernacular first; classical Han secondary; never lead with raw engine id. */
export function CitationCard({
  citationId,
  han,
  bachThoai,
  dich,
  locator,
  source,
}: CitationCardProps) {
  const { t, locale } = useLocale();
  const showDich =
    dich &&
    (locale === "en" ||
      !/Retrieved classical|Educational|local \/ stub/i.test(dich));

  // Prefer vernacular; if only engine-ish latin id, try display name
  const vernacular =
    bachThoai ||
    (han && /[\u4e00-\u9fff]/.test(han) ? undefined : displayPatternName(han || "", locale));

  const classical = han && /[\u4e00-\u9fff]/.test(han) ? han : undefined;

  return (
    <article data-testid="citation-card" id={citationId ? `cite-${citationId}` : undefined} className="cs-card cs-citation-card">
      {source ? <div className="cs-citation-card__source">{source}</div> : null}
      {vernacular ? (
        <p data-testid="cite-bach">
          <strong>{t("chart.citationVernacular")}:</strong> {vernacular}
        </p>
      ) : null}
      {classical ? (
        <p data-testid="cite-han" className="cs-citation-card__han">
          <strong>{t("chart.citationHan")}:</strong> {classical}
        </p>
      ) : han && !classical && !vernacular ? (
        <p data-testid="cite-han" className="cs-citation-card__han">
          <strong>{t("chart.citationHan")}:</strong> {displayPatternName(han, locale)}
        </p>
      ) : null}
      {showDich ? (
        <p data-testid="cite-dich">
          <strong>{t("chart.citationGloss")}:</strong> {dich}
        </p>
      ) : null}
      {locator ? (
        <p data-testid="cite-locator" className="cs-muted">
          {locator}
        </p>
      ) : null}
    </article>
  );
}
