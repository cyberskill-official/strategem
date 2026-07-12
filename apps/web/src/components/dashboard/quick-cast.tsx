"use client";

import Link from "next/link";

export function QuickCast() {
  return (
    <div data-testid="quick-cast">
      <Link
        href="/cast"
        data-testid="quick-cast-button"
        style={{
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          height: 44,
          minHeight: 44,
          padding: "0 20px",
          background: "var(--color-ochre, #F4BA17)",
          color: "var(--color-fg, #45210E)",
          borderRadius: 8,
          fontWeight: 600,
          textDecoration: "none",
        }}
      >
        Cast a chart
      </Link>
    </div>
  );
}
