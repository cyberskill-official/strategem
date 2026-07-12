"""Query/chart/report persistence — FR-API-004."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

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
        return PersistResult(query_id=query_id, chart_ids=chart_ids, report_id=report_id)
