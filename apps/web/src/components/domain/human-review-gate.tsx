"use client";

import { useState } from "react";
import { HumanReviewGate as DsHumanReviewGate } from "../../ds";
import { useLocale } from "../i18n/locale-provider";

export type HumanReviewGateProps = {
  riskLabel: string;
  summary?: string;
  onApprove?: () => void;
  onReject?: () => void;
};

/**
 * Human-in-the-loop checkpoint — delegates to the real @cyberskill/design
 * HumanReviewGate (via src/ds), which owns the `.cs-review-gate` warning
 * panel (risk label, summary, Approve / Reject). Product copy stays here,
 * localized en/vi/zh via useLocale and passed as props. The decision status
 * line is app-owned (DS has no post-decision state) and announced via
 * aria-live.
 */
export function HumanReviewGate({
  riskLabel,
  summary,
  onApprove,
  onReject,
}: HumanReviewGateProps) {
  const { t } = useLocale();
  const [status, setStatus] = useState<"idle" | "approved" | "rejected">("idle");
  return (
    <div data-testid="human-review-gate">
      <DsHumanReviewGate
        risk={
          <>
            <span aria-hidden>⚠ </span>
            {t("review.risk")}: {riskLabel}
          </>
        }
        summary={summary ?? ""}
        approveLabel={t("review.approve")}
        rejectLabel={t("review.reject")}
        onApprove={() => {
          setStatus("approved");
          onApprove?.();
        }}
        onReject={() => {
          setStatus("rejected");
          onReject?.();
        }}
      />
      <div aria-live="polite" className="cs-review-gate__reviewer" style={{ marginTop: 6 }}>
        {status === "idle" ? t("review.awaiting") : t("review.status", { status })}
      </div>
    </div>
  );
}
