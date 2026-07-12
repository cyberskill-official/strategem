"use client";

import { locales } from "../../i18n/routing";
import { useLocale } from "./locale-provider";

export type { Locale } from "../../i18n/routing";

export function LocaleSwitcher() {
  const { locale, setLocale, t } = useLocale();
  return (
    <label className="cs-locale-switcher">
      <span className="visually-hidden">{t("locale.label")}</span>
      <select
        aria-label={t("locale.label")}
        value={locale}
        onChange={(e) => setLocale(e.target.value as typeof locale)}
        data-testid="locale-switcher"
      >
        {locales.map((l) => (
          <option key={l} value={l}>
            {t(`locale.${l}`)}
          </option>
        ))}
      </select>
    </label>
  );
}
