"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { setAccessToken, setSessionUser } from "../../src/lib/auth/session";

export default function LoginPage() {
  const { t } = useLocale();
  const router = useRouter();
  const formId = useId();
  const errorId = `${formId}-error`;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data?.error?.message || data?.detail?.error?.message || t("auth.error"));
        return;
      }
      if (data.access) setAccessToken(data.access);
      setSessionUser({ email });
      router.push("/dashboard");
    } catch {
      setError(t("auth.errorNetwork"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cs-page cs-reveal" data-testid="login-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("auth.kicker")}</p>
        <h1>{t("auth.loginTitle")}</h1>
        <p className="cs-lead-short">{t("auth.loginSubtitle")}</p>
      </header>
      <form
        className="cs-card cs-auth-card cs-form-stack"
        onSubmit={onSubmit}
        data-testid="login-form"
        aria-busy={loading}
      >
        {error ? (
          <p role="alert" id={errorId} data-testid="login-error" className="cs-form-error">
            {error}
          </p>
        ) : null}
        <label htmlFor={`${formId}-email`}>
          <span>{t("auth.email")}</span>
          <input
            id={`${formId}-email`}
            type="email"
            required
            value={email}
            onChange={(ev) => setEmail(ev.target.value)}
            data-testid="login-email"
            autoComplete="email"
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? errorId : undefined}
          />
        </label>
        <label htmlFor={`${formId}-password`}>
          <span>{t("auth.password")}</span>
          <input
            id={`${formId}-password`}
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(ev) => setPassword(ev.target.value)}
            data-testid="login-password"
            autoComplete="current-password"
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? errorId : undefined}
          />
        </label>
        <button
          type="submit"
          className="cs-link-btn cs-link-btn--primary"
          disabled={loading}
          data-testid="login-submit"
          aria-busy={loading}
        >
          {loading ? t("auth.loading") : t("auth.loginSubmit")}
        </button>
      </form>
      <p className="cs-muted cs-auth-footer">
        {t("auth.noAccount")}{" "}
        <Link href="/signup" data-testid="login-to-signup">
          {t("auth.signupLink")}
        </Link>
      </p>
      <p className="cs-muted cs-auth-note">{t("auth.freeCastNote")}</p>
    </div>
  );
}
