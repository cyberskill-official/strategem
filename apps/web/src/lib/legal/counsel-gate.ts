/**
 * LEGAL-004 counsel sign-off gate — machine-readable status for release checks
 * and the in-product banner. Verdict stays `pending` until a human lawyer
 * records approval in docs/legal/vn-legal-review/counsel-signoff-record.md.
 *
 * Do NOT flip this to approved from agent work — only a recorded counsel
 * sign-off may change the verdict.
 */
export type CounselVerdict = "pending" | "approved" | "approved-with-conditions" | "rejected";

export type CounselGateStatus = {
  task: "LEGAL-004";
  counsel_review: "pending" | "approved";
  verdict: CounselVerdict;
  recordPath: string;
  gatePath: string;
};

/** Canonical in-repo status — mirrors docs/legal/vn-legal-review/gate-status.json. */
export const COUNSEL_GATE_STATUS: CounselGateStatus = {
  task: "LEGAL-004",
  counsel_review: "pending",
  verdict: "pending",
  recordPath: "docs/legal/vn-legal-review/counsel-signoff-record.md",
  gatePath: "docs/legal/vn-legal-review/sign-off-gate.md",
};

export function counselReviewStatus(): CounselGateStatus {
  return COUNSEL_GATE_STATUS;
}

export function isLaunchBlockedByCounsel(status: CounselGateStatus = COUNSEL_GATE_STATUS): boolean {
  return status.verdict !== "approved" && status.verdict !== "approved-with-conditions";
}
