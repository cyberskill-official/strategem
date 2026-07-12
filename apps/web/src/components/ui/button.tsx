import type { ButtonHTMLAttributes, ReactNode } from "react";

type Size = "xs" | "md";
type Variant = "primary" | "secondary" | "danger" | "accent";

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
};

/**
 * CyberSkill Button — primary = umber, accent = ochre highlight.
 * Min touch target 44px for md (CS control height).
 */
export function Button({
  variant = "primary",
  size = "md",
  children,
  disabled,
  className,
  style,
  type = "button",
  ...rest
}: ButtonProps) {
  if (variant === "primary" && size === "xs") {
    throw new Error("primary Button cannot use xs size (min touch target)");
  }
  const height =
    size === "md" ? "var(--control-height-md)" : "var(--control-height-xs)";

  let bg = "var(--cs-button-primary-bg)";
  let color = "var(--cs-button-primary-fg)";
  let border = "1px solid transparent";

  if (variant === "accent") {
    bg = "var(--color-ochre)";
    color = "var(--cs-button-accent-fg)";
  } else if (variant === "secondary") {
    bg = "var(--color-surface)";
    color = "var(--color-fg)";
    border = "1px solid var(--color-border)";
  } else if (variant === "danger") {
    bg = "var(--color-danger)";
    color = "var(--cs-color-text-inverse)";
  } else {
    // primary — umber fill; ochre is reserved for focus/accent (DS anchors)
    bg = "var(--cs-button-primary-bg)";
    color = "var(--cs-button-primary-fg)";
  }

  return (
    <button
      type={type}
      disabled={disabled}
      className={className}
      {...rest}
      style={{
        height,
        minHeight: height,
        background: bg,
        color,
        borderRadius: "var(--radius-md)",
        border,
        paddingInline: "var(--space-4)",
        lineHeight: "var(--line-height-control)",
        boxShadow: variant === "primary" || variant === "accent" ? "var(--shadow-sm)" : undefined,
        outlineColor: "var(--color-ochre-focus)",
        cursor: disabled ? "not-allowed" : "pointer",
        fontWeight: 600,
        fontFamily: "inherit",
        opacity: disabled ? 0.55 : 1,
        ...style,
      }}
    >
      {children}
    </button>
  );
}
