import { AIDisclosureBadge } from "../src/components/domain/ai-disclosure-badge";
import { HumanReviewGate } from "../src/components/domain/human-review-gate";
import { Button } from "../src/components/ui/button";

export default function HomePage() {
  return (
    <div>
      <h1 className="vn-text">Chiến lược Tam Thức</h1>
      <p className="vn-text">Hỗ trợ quyết định · Ẩn/Hiện · Ứng dụng</p>
      <div style={{ display: "flex", gap: "var(--space-3)", marginBlock: "var(--space-4)" }}>
        <Button>Primary action</Button>
        <AIDisclosureBadge
          model="rules-fallback"
          limits="Cited patterns only"
          citations={["yba_1"]}
          reviewStatus="not_required"
        />
      </div>
      <HumanReviewGate riskLabel="High cultural sensitivity" />
    </div>
  );
}
