"""In-memory repositories for FR-API-004 (swap for Postgres + RLS in prod)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import uuid4


class QueryRepo(Protocol):
    def create(self, user_id: str, req: dict[str, Any], systems: list[str]) -> str: ...

    def get(self, query_id: str) -> dict[str, Any] | None: ...

    def save_result(self, query_id: str, result: dict[str, Any]) -> None: ...


class ChartRepo(Protocol):
    def create(
        self,
        query_id: str,
        system: str,
        chart: dict[str, Any],
        patterns: list[Any],
    ) -> str: ...

    def get(self, chart_id: str) -> dict[str, Any] | None: ...

    def list_by_query(self, query_id: str) -> list[dict[str, Any]]: ...


class ReportRepo(Protocol):
    def create(
        self,
        query_id: str,
        user_id: str,
        report_data: dict[str, Any],
        pdf_path: str | None,
    ) -> str: ...

    def get(self, report_id: str, user_id: str) -> dict[str, Any] | None: ...


@dataclass
class InMemoryQueryRepo:
    rows: list[dict[str, Any]] = field(default_factory=list)
    results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def create(self, user_id: str, req: dict[str, Any], systems: list[str]) -> str:
        qid = str(uuid4())
        self.rows.append(
            {
                "id": qid,
                "user_id": user_id,
                "query_type": req.get("question_type", "unknown"),
                "input_data": req,
                "systems_used": systems,
            }
        )
        return qid

    def get(self, query_id: str) -> dict[str, Any] | None:
        for r in self.rows:
            if r["id"] == query_id:
                out = dict(r)
                if query_id in self.results:
                    out["result"] = self.results[query_id]
                return out
        return None

    def save_result(self, query_id: str, result: dict[str, Any]) -> None:
        self.results[query_id] = result


@dataclass
class InMemoryChartRepo:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def create(
        self,
        query_id: str,
        system: str,
        chart: dict[str, Any],
        patterns: list[Any],
    ) -> str:
        cid = str(uuid4())
        # store envelope object identity-preserving copy (json-roundtrip ok for tests)
        self.rows.append(
            {
                "id": cid,
                "query_id": query_id,
                "system": system,
                "chart_data": chart,
                "patterns_detected": patterns,
            }
        )
        return cid

    def get(self, chart_id: str) -> dict[str, Any] | None:
        for r in self.rows:
            if r["id"] == chart_id:
                return r
        return None

    def list_by_query(self, query_id: str) -> list[dict[str, Any]]:
        return [r for r in self.rows if r["query_id"] == query_id]


@dataclass
class InMemoryReportRepo:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def create(
        self,
        query_id: str,
        user_id: str,
        report_data: dict[str, Any],
        pdf_path: str | None,
    ) -> str:
        rid = str(uuid4())
        self.rows.append(
            {
                "id": rid,
                "query_id": query_id,
                "user_id": user_id,
                "report_data": report_data,
                "pdf_path": pdf_path,
            }
        )
        return rid

    def get(self, report_id: str, user_id: str) -> dict[str, Any] | None:
        for r in self.rows:
            if r["id"] == report_id and r["user_id"] == user_id:
                return r
        return None
