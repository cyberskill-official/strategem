import type { ButtonHTMLAttributes, ReactNode } from "react";

type Size = "xs" | "md";
type Variant = "primary" | "secondary" | "danger";

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
};

export function Button({
  variant = "primary",
  size = "md",
  children,
  disabled,
  ...rest
}: ButtonProps) {
  if (variant === "primary" && size === "xs") {
    throw new Error("primary Button cannot use xs size (min touch target)");
  }
  const height =
    size === "md" ? "var(--control-height-md)" : "var(--control-height-xs)";
  const bg =
    variant === "primary"
      ? "var(--color-ochre)"
      : variant === "danger"
        ? "var(--color-danger)"
        : "var(--color-surface)";
  const color =
    variant === "secondary" ? "var(--color-fg)" : "var(--color-fg)";
  return (
    <button
      type="button"
      disabled={disabled}
      {...rest}
      style={{
        height,
        minHeight: height,
        background: bg,
        color,
        borderRadius: "var(--radius-md)",
        border: "1px solid var(--color-border)",
        paddingInline: "var(--space-4)",
        lineHeight: "var(--line-height-control)",
        boxShadow: variant === "primary" ? "var(--shadow-sm)" : undefined,
        outlineColor: "var(--color-ochre-focus)",
        cursor: disabled ? "not-allowed" : "pointer",
      }}
    >
      {children}
    </button>
  );
}
