"""Query/chart/report persistence — FR-API-004."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tamthuc_api.repositories import (
    ChartRepo,
    InMemoryChartRepo,
    InMemoryQueryRepo,
    InMemoryReportRepo,
    QueryRepo,
    ReportRepo,
)


@dataclass
class PersistResult:
    query_id: str
    chart_ids: list[str] = field(default_factory=list)
    report_id: str | None = None


@dataclass
class PersistenceService:
    queries: QueryRepo = field(default_factory=InMemoryQueryRepo)
    charts: ChartRepo = field(default_factory=InMemoryChartRepo)
    reports: ReportRepo = field(default_factory=InMemoryReportRepo)
    fail_next: bool = False

    def persist_query_result(
        self,
        user_id: str,
        req: dict[str, Any],
        charts: dict[str, Any],
        patterns: list[Any],
        report: dict[str, Any] | None = None,
        *,
        full_result: dict[str, Any] | None = None,
    ) -> PersistResult:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("db write failed")

        # strip secrets from input_data
        safe_req = {k: v for k, v in req.items() if k not in ("password", "token")}
        systems = list(charts.keys())
        query_id = self.queries.create(user_id, safe_req, systems)
        chart_ids: list[str] = []
        for system, envelope in charts.items():
            # store envelope verbatim — no re-derivation
            cid = self.charts.create(query_id, system, envelope, patterns)
            chart_ids.append(cid)
        report_id = None
        if report is not None:
            report_id = self.reports.create(query_id, user_id, report, None)
        if full_result is not None:
            # attach assigned query_id into stored payload
            stored = dict(full_result)
            stored["query_id"] = query_id
            self.queries.save_result(query_id, stored)
        return PersistResult(query_id=query_id, chart_ids=chart_ids, report_id=report_id)

    def get_query_result(self, query_id: str) -> dict[str, Any] | None:
        row = self.queries.get(query_id)
        if row is None:
            return None
        result = row.get("result")
        if isinstance(result, dict):
            return result
        # rebuild from charts if full result missing
        charts_rows = self.charts.list_by_query(query_id)
        if not charts_rows:
            return None
        charts = {r["system"]: r["chart_data"] for r in charts_rows}
        patterns = charts_rows[0].get("patterns_detected") or []
        return {
            "query_id": query_id,
            "charts": charts,
            "patterns": patterns,
            "interpretation": None,
            "ai_disclosure": None,
        }

    def list_history(
        self,
        *,
        user_id: str | None = None,
        he: str | None = None,
        question_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        return self.queries.list_queries(
            user_id=user_id,
            he=he,
            question_type=question_type,
            limit=limit,
        )

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        row = self.reports.get_by_id(report_id)
        if row is None:
            return None
        data = row.get("report_data")
        if isinstance(data, dict):
            out = dict(data)
            out.setdefault("report_id", row["id"])
            out.setdefault("query_id", row.get("query_id"))
            return out
        return None
