export const locales = ["vi", "en", "zh"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "vi";

/** Locales that require dir="rtl" (none for zh; scaffold for future ar etc.). */
export const rtlLocales = [] as const satisfies readonly Locale[];

export function textDirection(locale: Locale): "ltr" | "rtl" {
  return (rtlLocales as readonly string[]).includes(locale) ? "rtl" : "ltr";
}

export const routing = {
  locales,
  defaultLocale,
  localePrefix: "as-needed" as const,
};
