"use client";

export type Persona = "beginner" | "expert";

export function PersonaToggle({
  value,
  onChange,
}: {
  value: Persona;
  onChange: (p: Persona) => void;
}) {
  return (
    <div
      role="group"
      aria-label="Persona"
      data-testid="persona-toggle"
      style={{ display: "inline-flex", gap: 4 }}
    >
      {(["beginner", "expert"] as const).map((p) => (
        <button
          key={p}
          type="button"
          aria-pressed={value === p}
          onClick={() => onChange(p)}
          style={{
            padding: "4px 10px",
            borderRadius: 6,
            border:
              value === p
                ? "2px solid var(--color-ochre, #c4a35a)"
                : "1px solid var(--color-border)",
            background: "var(--color-surface)",
            cursor: "pointer",
          }}
        >
          {p}
        </button>
      ))}
    </div>
  );
}
