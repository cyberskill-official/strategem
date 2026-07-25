"use client";

import { AIDisclosureBadge as DsAIDisclosureBadge } from "../../ds";
import { useLocale } from "../i18n/locale-provider";

export type AIDisclosureBadgeProps = {
  model: string;
  limits: string;
  citations: string[];
  reviewStatus?: "pending" | "not_required" | "approved" | "rejected";
};

/**
 * AI disclosure — delegates to the real @cyberskill/design AIDisclosureBadge
 * (via src/ds), which owns the `.cs-ai-disclosure` pill/panel markup. Product
 * content stays here and is richer than the DS default: model, limits,
 * citations and the human-review status, localized VI-first (en/vi/zh).
 * The DS `sources` prop is not used because its "Sources:" prefix is
 * hardcoded English; the localized citations line rides in `details` instead.
 */
export function AIDisclosureBadge({
  model,
  limits,
  citations,
  reviewStatus = "not_required",
}: AIDisclosureBadgeProps) {
  const { t } = useLocale();
  return (
    <DsAIDisclosureBadge
      label={`${t("disclosure.ai")} · ${t(`disclosure.status.${reviewStatus}`)}`}
      details={
        <>
          <span className="cs-ai-disclosure__details">
            <strong>{t("disclosure.model")}:</strong> {model}
          </span>
          <span className="cs-ai-disclosure__details">
            <strong>{t("disclosure.limits")}:</strong> {limits}
          </span>
          <span className="cs-ai-disclosure__sources">
            {t("disclosure.citations")}: {citations.join(", ") || "—"}
          </span>
        </>
      }
    />
  );
}
