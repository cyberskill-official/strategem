import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Button as DsButton, type ButtonProps as DsButtonProps } from "../../ds";

type Size = "xs" | "md";
type Variant = "primary" | "secondary" | "danger" | "accent";

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
};

/**
 * App Button — delegates to the real @cyberskill/design Button (via src/ds)
 * so DS owns the `.cs-button` markup contract (umber primary, ochre focus
 * ring, ≥44px touch target at md). App-level policy kept here: the narrower
 * variant/size menu, the primary+xs guard, and the `accent` variant, which is
 * app-owned (`.cs-button--accent` in styles/wow.css rides DS button tokens —
 * DS interpolates the variant into the class name, so it passes through).
 */
export function Button({
  variant = "primary",
  size = "md",
  children,
  ...rest
}: ButtonProps) {
  if (variant === "primary" && size === "xs") {
    throw new Error("primary Button cannot use xs size (min touch target)");
  }
  return (
    <DsButton variant={variant as DsButtonProps["variant"]} size={size} {...rest}>
      {children}
    </DsButton>
  );
}
