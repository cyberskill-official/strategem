"""Query/chart/report persistence — TASK-API-004 + COV-010 Postgres default."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from tamthuc_api.pg_store import PgQueryStore, database_url, require_database_or_memory
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
    # COV-010: optional Postgres full-result store
    pg: PgQueryStore | None = None
    backend: str = "memory"

    @classmethod
    def from_env(cls) -> PersistenceService:
        """Postgres when DATABASE_URL set; memory for dev/test; fail-closed in prod."""
        mode = require_database_or_memory()
        if mode == "postgres":
            dsn = database_url()
            assert dsn
            return cls(pg=PgQueryStore(dsn=dsn), backend="postgres")
        return cls(backend="memory")

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

        if self.pg is not None and full_result is not None:
            stored = dict(full_result)
            report_id: str | None = None
            if report is not None:
                raw_rid = report.get("report_id") or stored.get("report_id")
                report_id = str(raw_rid) if raw_rid is not None else None
                stored.setdefault("report", report)
                if report_id:
                    stored["report_id"] = report_id
            else:
                raw_rid = stored.get("report_id")
                report_id = str(raw_rid) if raw_rid is not None else None
            qid = self.pg.create(
                user_id,
                safe_req,
                systems,
                stored,
                query_id=str(stored["query_id"]) if stored.get("query_id") else None,
            )
            return PersistResult(query_id=qid, chart_ids=list(systems), report_id=report_id)
        if self.pg is not None and full_result is None:
            # still store a minimal payload so cast history survives
            minimal: dict[str, Any] = {"charts": charts, "patterns": patterns}
            report_id = None
            if report is not None:
                minimal["report"] = report
                raw_rid = report.get("report_id")
                report_id = str(raw_rid) if raw_rid is not None else None
                if report_id:
                    minimal["report_id"] = report_id
            qid = self.pg.create(user_id, safe_req, systems, minimal)
            return PersistResult(
                query_id=qid,
                chart_ids=list(systems),
                report_id=report_id,
            )

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

    def get_query_result(
        self, query_id: str, *, user_id: str | None = None
    ) -> dict[str, Any] | None:
        if self.pg is not None:
            return self.pg.get(query_id, user_id=user_id)
        row = self.queries.get(query_id)
        if row is None:
            return None
        if user_id is not None and row.get("user_id") != user_id:
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
        if self.pg is not None:
            return self.pg.list_queries(
                user_id=user_id,
                he=he,
                question_type=question_type,
                limit=limit,
            )
        return self.queries.list_queries(
            user_id=user_id,
            he=he,
            question_type=question_type,
            limit=limit,
        )

    def get_report(self, report_id: str, *, user_id: str | None = None) -> dict[str, Any] | None:
        """Lookup by report id or cast query id while preserving owner scoping."""
        if self.pg is not None:
            return self.pg.get_report(report_id, user_id=user_id)
        row = self.reports.get_by_id(report_id)
        if row is None:
            row = self.reports.get_by_query_id(report_id)
        if row is not None and user_id is not None and row.get("user_id") != user_id:
            return None
        if row is None:
            result = self.get_query_result(report_id, user_id=user_id)
            if isinstance(result, dict):
                embedded = result.get("report")
                if isinstance(embedded, dict):
                    out = dict(embedded)
                    out.setdefault("report_id", result.get("report_id") or out.get("report_id"))
                    out.setdefault("query_id", result.get("query_id") or report_id)
                    return out
            return None
        data = row.get("report_data")
        if isinstance(data, dict):
            out = dict(data)
            out.setdefault("report_id", row["id"])
            out.setdefault("query_id", row.get("query_id"))
            return out
        return None

    def save_result(self, query_id: str, result: dict[str, Any]) -> None:
        """Upsert full result after final id assignment (memory or Postgres)."""
        if self.pg is not None:
            systems = list((result.get("charts") or {}).keys())
            self.pg.create(
                str(result.get("user_id") or "anon"),
                {"question_type": (result.get("request") or {}).get("question_type")},
                systems,
                result,
                query_id=query_id,
            )
            return
        self.queries.save_result(query_id, result)


# silence unused import if tooling only uses from_env
_ = os
