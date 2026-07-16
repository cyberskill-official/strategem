"""In-memory repositories for TASK-API-004 (swap for Postgres + RLS in prod)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import uuid4


class QueryRepo(Protocol):
    def create(self, user_id: str, req: dict[str, Any], systems: list[str]) -> str: ...

    def get(self, query_id: str) -> dict[str, Any] | None: ...

    def save_result(self, query_id: str, result: dict[str, Any]) -> None: ...

    def list_queries(
        self,
        *,
        user_id: str | None = None,
        he: str | None = None,
        question_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]: ...


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

    def get_by_id(self, report_id: str) -> dict[str, Any] | None: ...


@dataclass
class InMemoryQueryRepo:
    rows: list[dict[str, Any]] = field(default_factory=list)
    results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def create(self, user_id: str, req: dict[str, Any], systems: list[str]) -> str:
        from datetime import UTC, datetime

        qid = str(uuid4())
        self.rows.append(
            {
                "id": qid,
                "user_id": user_id,
                "query_type": req.get("question_type", "unknown"),
                "input_data": req,
                "systems_used": systems,
                "created_at": datetime.now(UTC).isoformat(),
                "report_id": None,
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
        rid = result.get("report_id")
        if rid:
            for r in self.rows:
                if r["id"] == query_id:
                    r["report_id"] = rid
                    break

    def list_queries(
        self,
        *,
        user_id: str | None = None,
        he: str | None = None,
        question_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for r in reversed(self.rows):
            if user_id is not None and r.get("user_id") != user_id:
                continue
            if question_type and r.get("query_type") != question_type:
                continue
            systems = list(r.get("systems_used") or [])
            he_val = systems[0] if systems else ""
            # map system key to he-ish label for filters
            he_map = {"qimen": "ky_mon", "liuren": "luc_nham", "taiyi": "thai_at"}
            he_label = he_map.get(he_val, he_val)
            if he and he not in (he_val, he_label) and he not in systems:
                continue
            res = self.results.get(r["id"]) or {}
            out.append(
                {
                    "query_id": r["id"],
                    "he": he_label or he_val,
                    "question_type": r.get("query_type") or "unknown",
                    "created_at": r.get("created_at") or "",
                    "report_id": r.get("report_id") or res.get("report_id"),
                    "user_id": r.get("user_id"),
                }
            )
            if len(out) >= limit:
                break
        return out


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
        rid = str(report_data.get("report_id") or uuid4())
        data = dict(report_data)
        data["report_id"] = rid
        data["query_id"] = query_id
        self.rows.append(
            {
                "id": rid,
                "query_id": query_id,
                "user_id": user_id,
                "report_data": data,
                "pdf_path": pdf_path,
            }
        )
        return rid

    def get(self, report_id: str, user_id: str) -> dict[str, Any] | None:
        for r in self.rows:
            if r["id"] == report_id and r["user_id"] == user_id:
                return r
        return None

    def get_by_id(self, report_id: str) -> dict[str, Any] | None:
        for r in self.rows:
            if r["id"] == report_id:
                return r
        return None
