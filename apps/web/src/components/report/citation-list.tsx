"use client";

import type { Citation } from "../../lib/api/report";
import { useLocale } from "../i18n/locale-provider";

export function CitationList({ citations }: { citations: Citation[] }) {
  const { t } = useLocale();
  return (
    <section data-testid="citation-list" aria-label={t("report.citations")}>
      <h3>{t("report.citations")}</h3>
      <ul>
        {citations.map((c, i) => (
          <li key={`${c.source}-${c.locator}-${i}`} data-testid="citation-card">
            <div className="cite-source">
              <strong>{c.source}</strong>
            </div>
            <div className="cite-locator" data-testid="cite-locator">
              {c.locator}
            </div>
            {c.han ? (
              <div className="cite-han" data-testid="cite-han">
                {c.han}
              </div>
            ) : null}
            {c.bach_thoai ? (
              <div className="cite-bach" data-testid="cite-bach">
                {c.bach_thoai}
              </div>
            ) : null}
            {c.dich ? (
              <div className="cite-dich" data-testid="cite-dich">
                {c.dich}
              </div>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
