"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { t as translate, type Locale } from "../../i18n/request";
import { defaultLocale, locales } from "../../i18n/routing";

type LocaleContextValue = {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

const COOKIE = "locale";
const MAX_AGE = 60 * 60 * 24 * 365;

function readCookieLocale(): Locale | null {
  if (typeof document === "undefined") return null;
  const m = document.cookie.match(/(?:^|;\s*)locale=([^;]+)/);
  const v = m?.[1];
  if (v && (locales as readonly string[]).includes(v)) return v as Locale;
  return null;
}

export function LocaleProvider({
  children,
  initialLocale = defaultLocale,
}: {
  children: ReactNode;
  initialLocale?: Locale;
}) {
  const [locale, setLocaleState] = useState<Locale>(initialLocale);

  useEffect(() => {
    const fromCookie = readCookieLocale();
    if (fromCookie && fromCookie !== locale) setLocaleState(fromCookie);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- hydrate once from cookie
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.cookie = `${COOKIE}=${locale};path=/;max-age=${MAX_AGE};SameSite=Lax`;
  }, [locale]);

  const setLocale = useCallback((l: Locale) => {
    if ((locales as readonly string[]).includes(l)) setLocaleState(l);
  }, []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) =>
      translate(key, locale, vars),
    [locale],
  );

  const value = useMemo(
    () => ({ locale, setLocale, t }),
    [locale, setLocale, t],
  );

  return (
    <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
  );
}

export function useLocale(): LocaleContextValue {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    // Safe fallback for tests / SSR edge cases
    return {
      locale: defaultLocale,
      setLocale: () => {},
      t: (key, vars) => translate(key, defaultLocale, vars),
    };
  }
  return ctx;
}
