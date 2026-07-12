import { defaultLocale, type Locale } from "./routing";
import vi from "../messages/vi.json";
import en from "../messages/en.json";
import zh from "../messages/zh.json";

const catalogs: Record<Locale, Record<string, string>> = {
  vi: vi as Record<string, string>,
  en: en as Record<string, string>,
  zh: zh as Record<string, string>,
};

export type { Locale };

export function getMessages(locale: Locale = defaultLocale): Record<string, string> {
  return catalogs[locale] ?? catalogs[defaultLocale];
}

/** Translate a key; falls back to Vietnamese, then `[missing:key]`. Supports `{var}` interpolation. */
export function t(
  key: string,
  locale: Locale = defaultLocale,
  vars?: Record<string, string | number>,
): string {
  const cat = getMessages(locale);
  let s = key in cat ? cat[key] : (catalogs.vi[key] ?? `[missing:${key}]`);
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      s = s.replaceAll(`{${k}}`, String(v));
    }
  }
  return s;
}
