import { QueryForm } from "../../src/components/query/query-form";

export default function CastPage() {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(280px, 360px) 1fr",
        gap: "var(--space-5)",
        minHeight: "70vh",
      }}
    >
      <section aria-label="Query input">
        <h1 style={{ fontSize: "var(--text-xl)", marginBottom: "var(--space-4)" }}>
          New cast
        </h1>
        <QueryForm system="qimen" />
      </section>
      <section
        aria-label="Results"
        style={{
          border: "1px solid var(--color-border)",
          borderRadius: "var(--radius-md)",
          padding: "var(--space-5)",
          color: "var(--color-ink-muted)",
        }}
      >
        Cast a chart to see results here.
      </section>
    </div>
  );
}
