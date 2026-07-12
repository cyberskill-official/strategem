"use client";

import Link from "next/link";

const FLOWS = [
  { id: "lookup", title: "Lookup", href: "/cast", desc: "Ask → cast → read" },
  { id: "learning", title: "Learning", href: "/dashboard", desc: "Curriculum & practice" },
  { id: "management", title: "Management", href: "/dashboard", desc: "History, flags, share" },
];

export function FlowEntryCards() {
  return (
    <section data-testid="flow-entry-cards">
      <h2>Flows</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 }}>
        {FLOWS.map((f) => (
          <Link
            key={f.id}
            href={f.href}
            data-flow={f.id}
            style={{
              border: "1px solid var(--color-border)",
              borderRadius: 8,
              padding: 16,
              textDecoration: "none",
              color: "inherit",
            }}
          >
            <div style={{ fontWeight: 600 }}>{f.title}</div>
            <div style={{ fontSize: 13, opacity: 0.8 }}>{f.desc}</div>
          </Link>
        ))}
      </div>
    </section>
  );
}
