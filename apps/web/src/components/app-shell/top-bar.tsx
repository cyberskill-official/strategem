export function TopBar({ title = "Tam Thuc Strategem" }: { title?: string }) {
  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        height: "var(--control-height-md)",
        paddingInline: "var(--space-4)",
        borderBottom: "1px solid var(--color-border)",
        background: "var(--color-surface)",
      }}
    >
      <span
        style={{
          color: "var(--color-brand-accent)",
          fontWeight: 700,
          lineHeight: "var(--line-height-control)",
        }}
      >
        {title}
      </span>
    </header>
  );
}
