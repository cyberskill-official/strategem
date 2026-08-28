"use client";

import { useSyncExternalStore } from "react";
import { useLocale } from "../i18n/locale-provider";
import { IconMoon, IconSun } from "../visual/story-icons";

type Theme = "light" | "dark";

function readTheme(): Theme {
  return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
}

/** The <html data-theme> attribute is the store; observe it for re-renders. */
function subscribeTheme(onChange: () => void): () => void {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributeFilter: ["data-theme"] });
  return () => observer.disconnect();
}

/** Light/dark switch — drives the @cyberskill/design theme axis via `data-theme`. */
export function ThemeToggle() {
  const { t } = useLocale();
  const theme = useSyncExternalStore<Theme>(subscribeTheme, readTheme, () => "light");

  function toggle() {
    const next: Theme = theme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem("cs-theme", next);
    } catch {
      /* private mode — theme just won't persist */
    }
  }

  return (
    <button
      type="button"
      className="cs-theme-toggle"
      onClick={toggle}
      aria-pressed={theme === "dark"}
      aria-label={t("theme.toggle")}
      title={theme === "dark" ? t("theme.light") : t("theme.dark")}
      data-testid="theme-toggle"
    >
      {theme === "dark" ? (
        <IconSun className="cs-icon cs-icon--sm" />
      ) : (
        <IconMoon className="cs-icon cs-icon--sm" />
      )}
    </button>
  );
}
