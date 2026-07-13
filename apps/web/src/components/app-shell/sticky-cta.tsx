"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLocale } from "../i18n/locale-provider";

export function StickyCta() {
  const { t } = useLocale();
  const path = usePathname() ?? "/";
  // hide on cast form-heavy page to avoid overlap
  if (path.startsWith("/cast") || path.startsWith("/pricing")) return null;

  // Hide on results too — primary actions already on page
  if (path.startsWith("/results")) return null;

  return (
    <div className="cs-sticky-cta" data-testid="sticky-cta">
      <Link href="/cast" className="cs-link-btn cs-link-btn--primary">
        {t("sticky.cast")}
      </Link>
      <Link href="/pricing" className="cs-link-btn cs-link-btn--accent">
        {t("sticky.pricing")}
      </Link>
    </div>
  );
}
