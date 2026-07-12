import { defaultLocale, type Locale } from "./routing";
import vi from "../messages/vi.json";
import en from "../messages/en.json";

const catalogs: Record<Locale, Record<string, string>> = {
  vi: vi as Record<string, string>,
  en: en as Record<string, string>,
};

export type { Locale };

export function getMessages(locale: Locale = defaultLocale): Record<string, string> {
  return catalogs[locale] ?? catalogs[defaultLocale];
}

export function t(key: string, locale: Locale = defaultLocale): string {
  const cat = getMessages(locale);
  if (key in cat) return cat[key];
  const fb = catalogs.vi[key];
  return fb ?? `[missing:${key}]`;
}
