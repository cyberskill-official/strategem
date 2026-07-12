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


@dataclass
class Orchestrator:
    core: CoreClient = field(default_factory=LocalCoreClient)
    engine: EngineClient = field(default_factory=default_engine)
    rule: RuleClient = field(default_factory=LocalRuleClient)
    rag: RagClient = field(default_factory=LocalRagClient)
    persistence: PersistenceService | None = None
    audit: AuditLog | None = None
    call_log: list[str] = field(default_factory=list)

    def calculate(self, system: str, body: dict[str, Any]) -> dict[str, Any]:
        # Merge school flags into lich payload for engines
        body = dict(body)
        if body.get("co_truong_phai") and "co_truong_phai" not in (body.get("flags") or {}):
            body.setdefault("flags", {})
            if isinstance(body["flags"], dict):
                body["flags"] = {**body["flags"], **(body.get("co_truong_phai") or {})}

        self.call_log.append("core")
        lich = self.core.tinh_lich_phap(body)
        # carry flags into engine
        if body.get("co_truong_phai"):
            lich = dict(lich)
            lich["co_truong_phai"] = body["co_truong_phai"]
        self.call_log.append("engine")
        chart = self.engine.cast(system, lich)
        envelope = chart
        self.call_log.append("rule")
        patterns = self.rule.match(envelope)
        self.call_log.append("rag")
        interpretation = self.rag.interpret(envelope, patterns)
        disclosure = interpretation.get("ai_disclosure")
        charts = {system: envelope}
        query_id = str(uuid4())

        report_dict: dict[str, Any] | None = None
        try:
            report_dict = build_report_dict(envelope, interpretation, patterns, query_id)
            self.call_log.append("report")
        except Exception:
            report_dict = None

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

        if self.persistence is not None:
            self.call_log.append("persist")
            pr = self.persistence.persist_query_result(
                body.get("user_id", "anon"),
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
                    # re-save with final ids
                    self.persistence.queries.save_result(query_id, result)
        if self.audit is not None:
            self.audit.audit(
                body.get("user_id"),
                AuditAction.chart_cast,
                {
                    "system": system,
                    "query_id": query_id,
                    "report_id": result.get("report_id"),
                },
            )
        return result

    def calculate_all(self, body: dict[str, Any]) -> dict[str, Any]:
        systems = body.get("systems") or ["qimen", "liuren", "taiyi"]
        charts: dict[str, Any] = {}
        for s in systems:
            self.call_log.append("core")
            lich = self.core.tinh_lich_phap(body)
            if body.get("co_truong_phai"):
                lich = dict(lich)
                lich["co_truong_phai"] = body["co_truong_phai"]
            self.call_log.append("engine")
            charts[s] = self.engine.cast(s, lich)
        first = next(iter(charts.values()))
        self.call_log.append("rule")
        patterns = self.rule.match(first)
        self.call_log.append("rag")
        interpretation = self.rag.interpret(first, patterns)
        query_id = str(uuid4())
        report_dict = None
        try:
            report_dict = build_report_dict(first, interpretation, patterns, query_id)
            self.call_log.append("report")
        except Exception:
            report_dict = None
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
        if self.persistence is not None:
            self.call_log.append("persist")
            pr = self.persistence.persist_query_result(
                body.get("user_id", "anon"),
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
                    self.persistence.queries.save_result(query_id, result)
        if self.audit is not None:
            self.audit.audit(
                body.get("user_id"),
                AuditAction.chart_cast,
                {"system": "all", "query_id": query_id},
            )
        return result
