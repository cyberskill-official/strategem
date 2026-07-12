"use client";

export type CitationCardProps = {
  citationId?: string;
  han?: string;
  bachThoai?: string;
  dich?: string;
  locator?: string;
  source?: string;
};

export function CitationCard({
  citationId,
  han,
  bachThoai,
  dich,
  locator,
  source,
}: CitationCardProps) {
  return (
    <article
      data-testid="citation-card"
      id={citationId ? `cite-${citationId}` : undefined}
      style={{
        border: "1px solid var(--color-border)",
        borderRadius: 8,
        padding: 12,
        marginBottom: 8,
      }}
    >
      {source && (
        <div style={{ fontWeight: 600, marginBottom: 4 }}>{source}</div>
      )}
      {han && (
        <p data-testid="cite-han" style={{ fontFamily: "serif" }}>
          <strong>漢:</strong> {han}
        </p>
      )}
      {bachThoai && (
        <p data-testid="cite-bach">
          <strong>Bạch thoại:</strong> {bachThoai}
        </p>
      )}
      {dich && (
        <p data-testid="cite-dich">
          <strong>Dịch:</strong> {dich}
        </p>
      )}
      {locator && (
        <p data-testid="cite-locator" style={{ fontSize: 12, opacity: 0.75 }}>
          {locator}
        </p>
      )}
    </article>
  );
}
