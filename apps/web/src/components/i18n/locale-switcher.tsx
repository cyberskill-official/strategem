"use client";

import { t, type Locale } from "../../i18n/request";
import { locales } from "../../i18n/routing";

// re-export Locale via routing for consumers
export type { Locale } from "../../i18n/routing";

export function LocaleSwitcher({
  locale,
  onChange,
}: {
  locale: Locale;
  onChange: (l: Locale) => void;
}) {
  return (
    <select
      aria-label="Locale"
      value={locale}
      onChange={(e) => onChange(e.target.value as Locale)}
      data-testid="locale-switcher"
    >
      {locales.map((l) => (
        <option key={l} value={l}>
          {t(`locale.${l}`, locale)}
        </option>
      ))}
    </select>
  );
}
