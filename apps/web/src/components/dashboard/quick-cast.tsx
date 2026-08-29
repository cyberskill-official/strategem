"use client";

import Link from "next/link";
import { useLocale } from "../i18n/locale-provider";

export function QuickCast() {
  const { t } = useLocale();
  return (
    <div data-testid="quick-cast">
      <Link
        href="/cast"
        data-testid="quick-cast-button"
        className="cs-link-btn cs-link-btn--accent"
      >
        {t("cast.button")}
      </Link>
    </div>
  );
}
