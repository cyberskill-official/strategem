"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useLocale } from "../../src/components/i18n/locale-provider";
import { setAccessToken, setSessionUser } from "../../src/lib/auth/session";

export default function SignupPage() {
  const { t } = useLocale();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/auth/signup", {
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
      setSessionUser({ email, user_id: data.user_id });
      router.push("/dashboard");
    } catch {
      setError(t("auth.errorNetwork"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cs-page cs-reveal" data-testid="signup-page">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("auth.kicker")}</p>
        <h1>{t("auth.signupTitle")}</h1>
        <p className="cs-lead-short">{t("auth.signupSubtitle")}</p>
      </header>
      <form className="cs-card" onSubmit={onSubmit} data-testid="signup-form">
        <label style={{ display: "block" }}>
          <span className="cs-muted">{t("auth.email")}</span>
          <input
            type="email"
            required
            value={email}
            onChange={(ev) => setEmail(ev.target.value)}
            data-testid="signup-email"
            autoComplete="email"
          />
        </label>
        <label style={{ display: "block", marginTop: "0.75rem" }}>
          <span className="cs-muted">{t("auth.password")}</span>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(ev) => setPassword(ev.target.value)}
            data-testid="signup-password"
            autoComplete="new-password"
          />
        </label>
        <p className="cs-muted" style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>
          {t("auth.birthNote")}
        </p>
        {error ? (
          <p role="alert" data-testid="signup-error" style={{ color: "var(--cs-danger, #a33)" }}>
            {error}
          </p>
        ) : null}
        <button
          type="submit"
          className="cs-link-btn cs-link-btn--primary"
          disabled={loading}
          data-testid="signup-submit"
          style={{ marginTop: "1rem" }}
        >
          {loading ? t("auth.loading") : t("auth.signupSubmit")}
        </button>
      </form>
      <p className="cs-muted" style={{ marginTop: "1rem" }}>
        {t("auth.hasAccount")}{" "}
        <Link href="/login" data-testid="signup-to-login">
          {t("auth.loginLink")}
        </Link>
      </p>
    </div>
  );
}
