"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLocale } from "../i18n/locale-provider";

export function StickyCta() {
  const { t } = useLocale();
  const path = usePathname() ?? "/";
  // hide on cast form-heavy page to avoid overlap
  if (path.startsWith("/cast") || path.startsWith("/pricing")) return null;

  return (
    <div className="cs-sticky-cta" data-testid="sticky-cta">
      <Link href="/cast" className="cs-link-btn cs-link-btn--primary" style={{ minHeight: 40 }}>
        {t("sticky.cast")}
      </Link>
      <Link href="/pricing" className="cs-link-btn cs-link-btn--accent" style={{ minHeight: 40 }}>
        {t("sticky.pricing")}
      </Link>
    </div>
  );
}
