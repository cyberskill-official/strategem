"use client";

import { useId, useState, type KeyboardEvent } from "react";

export type AIDisclosureBadgeProps = {
  model: string;
  limits: string;
  citations: string[];
  reviewStatus?: "pending" | "not_required" | "approved" | "rejected";
};

export function AIDisclosureBadge({
  model,
  limits,
  citations,
  reviewStatus = "not_required",
}: AIDisclosureBadgeProps) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const onKey = (e: KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setOpen((v) => !v);
    }
    if (e.key === "Escape") setOpen(false);
  };
  return (
    <span style={{ position: "relative", display: "inline-flex" }}>
      <button
        type="button"
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
        onKeyDown={onKey}
        style={{
          background: "var(--color-info)",
          color: "var(--color-bg)",
          borderRadius: "var(--radius-full)",
          border: "none",
          padding: "var(--space-2) var(--space-3)",
          fontSize: "var(--font-size-sm)",
          lineHeight: "var(--line-height-control)",
          cursor: "pointer",
        }}
      >
        AI · {reviewStatus}
      </button>
      {open ? (
        <div
          id={panelId}
          role="dialog"
          style={{
            position: "absolute",
            top: "110%",
            left: 0,
            zIndex: 10,
            minWidth: 240,
            background: "var(--color-surface)",
            color: "var(--color-fg)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-md)",
            padding: "var(--space-3)",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <p>
            <strong>Model:</strong> {model}
          </p>
          <p>
            <strong>Limits:</strong> {limits}
          </p>
          <p>
            <strong>Citations:</strong> {citations.join(", ") || "—"}
          </p>
        </div>
      ) : null}
    </span>
  );
}
