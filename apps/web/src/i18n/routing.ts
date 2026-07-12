export const locales = ["vi", "en"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "vi";

export const routing = {
  locales,
  defaultLocale,
  localePrefix: "as-needed" as const,
};
