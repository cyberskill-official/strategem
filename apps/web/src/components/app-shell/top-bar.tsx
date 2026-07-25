"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { LocaleSwitcher } from "../i18n/locale-switcher";
import { useLocale } from "../i18n/locale-provider";
import { ThemeToggle } from "./theme-toggle";

type NavItem = { href: string; key: string };

/** Primary journey stays visible; everything else is grouped (was a flat 15-link bar). */
const PRIMARY: readonly NavItem[] = [
  { href: "/", key: "nav.home" },
  { href: "/cast", key: "nav.cast" },
  { href: "/timing", key: "nav.timing" },
  { href: "/dashboard", key: "nav.dashboard" },
];

const EXPLORE: readonly NavItem[] = [
  { href: "/scenarios", key: "nav.scenarios" },
  { href: "/cross-system", key: "nav.cross" },
  { href: "/patterns", key: "nav.patterns" },
  { href: "/library", key: "nav.library" },
  { href: "/practice", key: "nav.practice" },
  { href: "/learn", key: "nav.learn" },
  { href: "/help", key: "nav.help" },
];

const ACCOUNT: readonly NavItem[] = [
  { href: "/pricing", key: "nav.pricing" },
  { href: "/manage/history", key: "nav.history" },
  { href: "/manage/settings", key: "nav.settings" },
  { href: "/login", key: "nav.login" },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Dropdown group using the DS .cs-menu contract — Esc / Arrow / Home / End. */
function NavMenu({
  label,
  items,
  pathname,
  testId,
}: {
  label: string;
  items: readonly NavItem[];
  pathname: string;
  testId: string;
}) {
  const { t } = useLocale();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);
  const menuId = useId();
  const groupActive = items.some((i) => isActive(pathname, i.href));

  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: globalThis.KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  useEffect(() => {
    if (!open || !ref.current) return;
    const first = ref.current.querySelector<HTMLElement>('[role="menuitem"]');
    first?.focus();
  }, [open]);

  function onTriggerKey(e: KeyboardEvent<HTMLButtonElement>) {
    if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setOpen(true);
    }
    if (e.key === "Escape") setOpen(false);
  }

  function onMenuKey(e: KeyboardEvent<HTMLDivElement>) {
    const nodes = Array.from(
      ref.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? [],
    );
    if (!nodes.length) return;
    const idx = nodes.indexOf(document.activeElement as HTMLElement);
    if (e.key === "ArrowDown") {
      e.preventDefault();
      nodes[(idx + 1) % nodes.length]?.focus();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      nodes[(idx - 1 + nodes.length) % nodes.length]?.focus();
    } else if (e.key === "Home") {
      e.preventDefault();
      nodes[0]?.focus();
    } else if (e.key === "End") {
      e.preventDefault();
      nodes[nodes.length - 1]?.focus();
    } else if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
      ref.current?.querySelector<HTMLButtonElement>("button")?.focus();
    }
  }

  return (
    <div className="cs-menu" ref={ref}>
      <button
        type="button"
        className="cs-nav-link cs-nav-link--menu"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        aria-current={groupActive ? "true" : undefined}
        onClick={() => setOpen((v) => !v)}
        onKeyDown={onTriggerKey}
        data-testid={testId}
      >
        {label} <span aria-hidden>▾</span>
      </button>
      {open ? (
        <div
          id={menuId}
          className="cs-menu__list"
          role="menu"
          onKeyDown={onMenuKey}
        >
          {items.map((item) => (
            <Link
              key={item.href}
              role="menuitem"
              href={item.href}
              className="cs-menu__item"
              tabIndex={0}
              aria-current={isActive(pathname, item.href) ? "page" : undefined}
              onClick={() => setOpen(false)}
            >
              {t(item.key)}
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function TopBar() {
  const { t } = useLocale();
  const pathname = usePathname() ?? "/";

  return (
    <header className="cs-topbar">
      <div className="cs-topbar__inner">
        <Link href="/" className="cs-brand" data-testid="app-brand">
          <span className="cs-brand__mark" aria-hidden />
          <span className="cs-brand__text">
            <span className="cs-brand__name">{t("app.name")}</span>
            <span className="cs-brand__tagline cs-muted">{t("app.slogan")}</span>
          </span>
        </Link>

        <nav className="cs-nav" aria-label={t("app.name")}>
          {PRIMARY.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="cs-nav-link"
              aria-current={isActive(pathname, item.href) ? "page" : undefined}
            >
              {t(item.key)}
            </Link>
          ))}
          <NavMenu
            label={t("nav.groupExplore")}
            items={EXPLORE}
            pathname={pathname}
            testId="nav-menu-explore"
          />
          <NavMenu
            label={t("nav.groupAccount")}
            items={ACCOUNT}
            pathname={pathname}
            testId="nav-menu-account"
          />
        </nav>

        <div className="cs-topbar__actions">
          <ThemeToggle />
          <LocaleSwitcher />
        </div>
      </div>
    </header>
  );
}
