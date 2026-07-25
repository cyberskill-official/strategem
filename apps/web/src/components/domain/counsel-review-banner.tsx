"use client";

import { counselReviewStatus } from "../../lib/legal/counsel-gate";
import { useLocale } from "../i18n/locale-provider";

/**
 * In-product LEGAL-004 gate hook — surfaces counsel_review status without
 * claiming sign-off has occurred. Pending = launch blocked (RISK-4).
 */
export function CounselReviewBanner() {
  const { t } = useLocale();
  const status = counselReviewStatus();
  if (status.verdict === "approved") return null;

  return (
    <aside
      className="cs-counsel-gate"
      data-testid="counsel-review-gate"
      data-counsel-verdict={status.verdict}
      role="status"
      aria-label={t("legal.counsel.label")}
    >
      <strong>{t("legal.counsel.label")}</strong>
      <span>{t("legal.counsel.pending")}</span>
    </aside>
  );
}
