"use client";

/**
 * COV-017 — palace/detail sidebar for interactive charts.
 * Read-only: shows stem/star/door/god + related patterns for selected seat.
 */

import { displayDomainTerm, displayPatternName } from "../../lib/domain/glossary";
import { useLocale } from "../i18n/locale-provider";
import type { PalaceCell } from "./qimen-nine-palace";
import type { PatternItem } from "../results/pattern-list";

export type PalaceDetailSidebarProps = {
  selected: number | null;
  cell?: PalaceCell | null;
  patterns?: PatternItem[];
  system?: "qimen" | "liuren" | "taiyi" | string;
  onClose?: () => void;
};

export function PalaceDetailSidebar({
  selected,
  cell,
  patterns = [],
  system = "qimen",
  onClose,
}: PalaceDetailSidebarProps) {
  const { t, locale } = useLocale();

  if (selected == null) {
    return (
      <aside
        className="cs-card"
        data-testid="palace-detail-empty"
        aria-label={t("palace.sidebar")}
      >
        <p className="cs-muted">{t("palace.pickHint")}</p>
      </aside>
    );
  }

  const related = patterns.filter(
    (p) => p.cung != null && Number(p.cung) === Number(selected),
  );

  const stem = cell?.stem;
  const star = displayDomainTerm(cell?.star, locale);
  const door = displayDomainTerm(cell?.door, locale);
  const god = displayDomainTerm(cell?.god, locale);

  return (
    <aside
      className="cs-card"
      data-testid="palace-detail-sidebar"
      aria-label={`${t("palace.sidebar")} ${selected}`}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>
          {t("chart.palace")} {selected}
        </h3>
        {onClose ? (
          <button
            type="button"
            className="cs-link-btn cs-link-btn--secondary"
            onClick={onClose}
            data-testid="palace-detail-close"
            aria-label={t("palace.close")}
          >
            ×
          </button>
        ) : null}
      </div>
      <p className="cs-muted" style={{ fontSize: "0.85rem" }}>
        {system}
      </p>
      <dl data-testid="palace-detail-fields" style={{ margin: "0.75rem 0" }}>
        {stem ? (
          <div>
            <dt className="cs-muted">{t("chart.stem")}</dt>
            <dd style={{ fontFamily: "serif", fontSize: "1.1rem" }}>{stem}</dd>
          </div>
        ) : null}
        {star ? (
          <div>
            <dt className="cs-muted">{t("chart.star")}</dt>
            <dd>{star}</dd>
          </div>
        ) : null}
        {door ? (
          <div>
            <dt className="cs-muted">{t("chart.door")}</dt>
            <dd>{door}</dd>
          </div>
        ) : null}
        {god ? (
          <div>
            <dt className="cs-muted">{t("chart.god")}</dt>
            <dd>{god}</dd>
          </div>
        ) : null}
        {!stem && !star && !door && !god ? (
          <p className="cs-muted">{t("palace.noCellData")}</p>
        ) : null}
      </dl>
      <h4>{t("palace.relatedPatterns")}</h4>
      {related.length === 0 ? (
        <p className="cs-muted" data-testid="palace-patterns-empty">
          {t("palace.noRelated")}
        </p>
      ) : (
        <ul data-testid="palace-related-patterns" style={{ paddingLeft: "1.1rem" }}>
          {related.map((p, i) => (
            <li key={p.id ?? `${p.name}-${i}`}>
              {displayPatternName(p.name, locale)}
              {p.polarity ? (
                <span className="cs-muted"> · {p.polarity}</span>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
