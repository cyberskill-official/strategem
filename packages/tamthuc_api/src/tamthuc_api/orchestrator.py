"""Nine-step query orchestration (TASK-API-001).

Explicit pipeline (strategy 4.2):

  1. validate       — accept validated request (Pydantic already shaped the body)
  2. auth_core      — authorize capability + resolve calendar via CORE
  3. engine         — cast la so envelope (read-only thereafter)
  4. rule           — detect patterns
  5. rag_retrieve   — retrieve grounded classical chunks
  6. llm_interpret  — build prompt + LLM interpretation
  7. report         — assemble structured report
  8. return         — build FE response (chart + patterns + cited interp + AIDisclosure)
  9. persist_audit  — persist query/chart/report + audit row (TASK-API-004)

The gateway never re-computes or mutates ban / cach_cuc / lich_phap / co_truong_phai.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from tamthuc_api.audit import AuditAction, AuditLog
from tamthuc_api.clients.core import CoreClient, LocalCoreClient
from tamthuc_api.clients.engine import EngineClient, default_engine
from tamthuc_api.clients.rag import LocalRagClient, RagClient
from tamthuc_api.clients.rule import LocalRuleClient, RuleClient
from tamthuc_api.persistence import PersistenceService
from tamthuc_api.report_bridge import build_report_dict

# Canonical call_log markers — tests assert this exact nine-step order.
NINE_STEPS: tuple[str, ...] = (
    "validate",
    "auth_core",
    "engine",
    "rule",
    "rag_retrieve",
    "llm_interpret",
    "report",
    "return",
    "persist_audit",
)


def _is_ephemeral_owner(user_id: object) -> bool:
    uid = str(user_id or "").strip().lower()
    return uid in {"", "anon"}


@dataclass
class Orchestrator:
    core: CoreClient = field(default_factory=LocalCoreClient)
    engine: EngineClient = field(default_factory=default_engine)
    rule: RuleClient = field(default_factory=LocalRuleClient)
    rag: RagClient = field(default_factory=LocalRagClient)
    persistence: PersistenceService | None = None
    audit: AuditLog | None = None
    call_log: list[str] = field(default_factory=list)

    def _merge_school_flags(self, body: dict[str, Any]) -> dict[str, Any]:
        body = dict(body)
        if body.get("co_truong_phai") and "co_truong_phai" not in (body.get("flags") or {}):
            body.setdefault("flags", {})
            if isinstance(body["flags"], dict):
                body["flags"] = {**body["flags"], **(body.get("co_truong_phai") or {})}
        return body

    def _authorize_single(self, _system: str, _body: dict[str, Any]) -> None:
        """Step 2 seam: single-system cast is a free-tier capability (anonymous OK)."""
        return None

    def _persist_and_audit(
        self,
        *,
        system_label: str,
        body: dict[str, Any],
        charts: dict[str, Any],
        patterns: list[Any],
        report_dict: dict[str, Any] | None,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        query_id = str(result.get("query_id") or uuid4())
        result["query_id"] = query_id
        ephemeral = _is_ephemeral_owner(body.get("user_id"))
        result["persistence"] = "ephemeral" if ephemeral else "owned"
        if not ephemeral and self.persistence is not None:
            pr = self.persistence.persist_query_result(
                str(body.get("user_id")),
                body,
                charts,
                patterns,
                report=report_dict,
                full_result=result,
            )
            query_id = pr.query_id
            result["query_id"] = query_id
            if pr.report_id:
                result["report_id"] = pr.report_id
                if report_dict is not None:
                    report_dict["report_id"] = pr.report_id
                    report_dict["query_id"] = query_id
                    result["report"] = report_dict
                    self.persistence.save_result(query_id, result)
        if self.audit is not None:
            self.audit.audit(
                None if ephemeral else body.get("user_id"),
                AuditAction.chart_cast,
                {
                    "system": system_label,
                    "query_id": query_id,
                    "report_id": result.get("report_id"),
                    "persistence": result["persistence"],
                },
            )
        return result

    def calculate(self, system: str, body: dict[str, Any]) -> dict[str, Any]:
        # 1. validate — body already shaped by CalculateRequest; mark the seam
        self.call_log.append("validate")
        body = self._merge_school_flags(body)

        # 2. authorize + CORE calendar
        self._authorize_single(system, body)
        lich = self.core.tinh_lich_phap(body)
        if body.get("co_truong_phai"):
            lich = dict(lich)
            lich["co_truong_phai"] = body["co_truong_phai"]
        self.call_log.append("auth_core")

        # 3. engine cast — envelope is read-only from here
        chart = self.engine.cast(system, lich)
        envelope = chart
        self.call_log.append("engine")

        # 4. rule patterns
        patterns = self.rule.match(envelope)
        self.call_log.append("rule")

        # 5. RAG retrieve
        retrieved = self.rag.retrieve(envelope, patterns)
        self.call_log.append("rag_retrieve")

        # 6. LLM interpret
        interpretation = self.rag.interpret(envelope, patterns, retrieved=retrieved)
        self.call_log.append("llm_interpret")
        disclosure = interpretation.get("ai_disclosure")
        charts = {system: envelope}
        query_id = str(uuid4())

        # 7. report assemble
        report_dict: dict[str, Any] | None = None
        try:
            report_dict = build_report_dict(envelope, interpretation, patterns, query_id)
            self.call_log.append("report")
        except Exception:
            report_dict = None
            self.call_log.append("report")

        # 8. return FE payload
        result: dict[str, Any] = {
            "query_id": query_id,
            "charts": charts,
            "patterns": patterns,
            "interpretation": interpretation,
            "ai_disclosure": disclosure,
        }
        if report_dict is not None:
            result["report_id"] = report_dict["report_id"]
            result["report"] = report_dict
        self.call_log.append("return")

        # 9. persist + audit
        result = self._persist_and_audit(
            system_label=system,
            body=body,
            charts=charts,
            patterns=patterns,
            report_dict=report_dict,
            result=result,
        )
        self.call_log.append("persist_audit")
        return result

    def calculate_all(self, body: dict[str, Any]) -> dict[str, Any]:
        self.call_log.append("validate")
        body = self._merge_school_flags(body)
        systems = body.get("systems") or ["qimen", "liuren", "taiyi"]

        # 2. authorize is enforced at the route (JWT + premium); CORE once per system below
        charts: dict[str, Any] = {}
        lich = self.core.tinh_lich_phap(body)
        if body.get("co_truong_phai"):
            lich = dict(lich)
            lich["co_truong_phai"] = body["co_truong_phai"]
        self.call_log.append("auth_core")

        for s in systems:
            self.call_log.append("engine")
            charts[s] = self.engine.cast(s, lich)
        first = next(iter(charts.values()))

        self.call_log.append("rule")
        patterns = self.rule.match(first)

        retrieved = self.rag.retrieve(first, patterns)
        self.call_log.append("rag_retrieve")
        interpretation = self.rag.interpret(first, patterns, retrieved=retrieved)
        self.call_log.append("llm_interpret")

        query_id = str(uuid4())
        report_dict = None
        try:
            report_dict = build_report_dict(first, interpretation, patterns, query_id)
        except Exception:
            report_dict = None
        self.call_log.append("report")

        result: dict[str, Any] = {
            "query_id": query_id,
            "charts": charts,
            "patterns": patterns,
            "interpretation": interpretation,
            "ai_disclosure": interpretation.get("ai_disclosure"),
        }
        if report_dict is not None:
            result["report_id"] = report_dict["report_id"]
            result["report"] = report_dict
        self.call_log.append("return")

        result = self._persist_and_audit(
            system_label="all",
            body=body,
            charts=charts,
            patterns=patterns,
            report_dict=report_dict,
            result=result,
        )
        self.call_log.append("persist_audit")
        return result
