"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useLocale } from "../../../src/components/i18n/locale-provider";
import { getModule, LEARN_MODULES } from "../../../src/lib/learn/modules";
import type { Locale } from "../../../src/i18n/routing";
import type { LessonBlock } from "../../../src/lib/learn/modules";

function Block({ b }: { b: LessonBlock }) {
  if (b.type === "h") return <h2 style={{ marginTop: 24 }}>{b.text}</h2>;
  if (b.type === "p") return <p className="cs-prose">{b.text}</p>;
  if (b.type === "callout")
    return <div className="cs-banner cs-banner--ochre">{b.text}</div>;
  if (b.type === "ul")
    return (
      <ul style={{ lineHeight: 1.7 }}>
        {b.items.map((it) => (
          <li key={it}>{it}</li>
        ))}
      </ul>
    );
  return null;
}

export default function LearnModulePage() {
  const params = useParams();
  const slug = String(params?.slug ?? "");
  const { t, locale } = useLocale();
  const loc = locale as Locale;
  const mod = getModule(slug);

  if (!mod) {
    return (
      <div className="cs-page">
        <h1>{t("learn.notFound")}</h1>
        <Link href="/learn">{t("learn.back")}</Link>
      </div>
    );
  }

  const body = mod.body[loc] ?? mod.body.vi;
  const others = LEARN_MODULES.filter((m) => m.slug !== mod.slug);

  return (
    <div className="cs-page cs-reveal" data-testid="learn-module">
      <p className="cs-kicker">
        <Link href="/learn" style={{ textDecoration: "none", color: "inherit" }}>
          {t("nav.learn")}
        </Link>
        {" · "}
        {mod.order}/3
      </p>
      <header className="cs-cast-intro" style={{ marginBottom: 8 }}>
        <span className="cs-visual-card__emoji" aria-hidden style={{ fontSize: "2rem" }}>
          {mod.glyph}
        </span>
        <h1 style={{ marginTop: 8 }}>{mod.title[loc] ?? mod.title.vi}</h1>
        <p className="cs-lead-short">{mod.summary[loc] ?? mod.summary.vi}</p>
      </header>

      <article className="cs-card" style={{ maxWidth: 720 }}>
        {body.map((b, i) => (
          <Block key={i} b={b} />
        ))}
      </article>

      <div className="cs-hero__actions" style={{ marginTop: 8 }}>
        <Link
          href={mod.practiceHref}
          className="cs-link-btn cs-link-btn--primary cs-link-btn--pulse"
        >
          {t("learn.practice")}
        </Link>
        <Link href="/learn" className="cs-link-btn cs-link-btn--secondary">
          {t("learn.back")}
        </Link>
      </div>

      <section style={{ marginTop: 24 }}>
        <h2>{t("learn.moreModules")}</h2>
        <div className="cs-grid-3">
          {others.map((m) => (
            <Link
              key={m.slug}
              href={`/learn/${m.slug}`}
              className="cs-visual-card"
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <span className="cs-visual-card__emoji" aria-hidden>
                {m.glyph}
              </span>
              <h3 style={{ margin: 0 }}>{m.title[loc] ?? m.title.vi}</h3>
              <p>{m.summary[loc] ?? m.summary.vi}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
