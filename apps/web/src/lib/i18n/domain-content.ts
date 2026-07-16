/**
 * Domain content plane (TASK-WEB-006): fetch expert translations from backend.
 * NEVER machine-translates; NEVER strips Han.
 */

export type DomainText = {
  han?: string;
  text: string;
  locale: string;
  source?: string;
};

export type DomainKind = "pattern" | "interpretation" | "excerpt";

export async function getDomainContent(
  kind: DomainKind,
  ref: string,
  locale: "vi" | "en",
  fetchImpl: typeof fetch = fetch,
  baseUrl = "",
): Promise<DomainText> {
  // Backend serves pre-translated domain content; UI never re-translates.
  const res = await fetchImpl(
    `${baseUrl}/api/v1/knowledge/domain?kind=${kind}&ref=${encodeURIComponent(ref)}&locale=${locale}`,
  );
  if (!res.ok) {
    // fallback to vi-shaped placeholder without MT
    return {
      han: ref,
      text: ref,
      locale: "vi",
      source: "fallback",
    };
  }
  const data = (await res.json()) as DomainText;
  // preserve han always
  return {
    han: data.han ?? ref,
    text: data.text,
    locale: data.locale ?? locale,
    source: data.source,
  };
}
