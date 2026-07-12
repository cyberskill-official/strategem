"use client";

export function RecommendationsList({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <section data-testid="recommendations-list" aria-label="Recommendations">
      <h3>Recommendations</h3>
      <ul>
        {items.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
    </section>
  );
}
