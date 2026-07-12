"use client";

import { useState } from "react";
import { Button } from "../ui/button";

export type HumanReviewGateProps = {
  riskLabel: string;
  onApprove?: () => void;
  onReject?: () => void;
};

export function HumanReviewGate({
  riskLabel,
  onApprove,
  onReject,
}: HumanReviewGateProps) {
  const [status, setStatus] = useState<"idle" | "approved" | "rejected">("idle");
  return (
    <section
      aria-label="Human review gate"
      style={{
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-md)",
        padding: "var(--space-4)",
        background: "var(--color-surface)",
      }}
    >
      <p style={{ color: "var(--color-warning)", marginBottom: "var(--space-2)" }}>
        <span aria-hidden>⚠ </span>
        <strong>Risk:</strong> {riskLabel}
      </p>
      <div style={{ display: "flex", gap: "var(--space-2)" }}>
        <Button
          variant="primary"
          onClick={() => {
            setStatus("approved");
            onApprove?.();
          }}
        >
          Approve
        </Button>
        <Button
          variant="danger"
          onClick={() => {
            setStatus("rejected");
            onReject?.();
          }}
        >
          <span aria-hidden>⛔ </span>
          Reject
        </Button>
      </div>
      <div aria-live="polite" style={{ marginTop: "var(--space-2)", color: "var(--color-muted)" }}>
        {status === "idle" ? "Awaiting human decision" : `Status: ${status}`}
      </div>
    </section>
  );
}
