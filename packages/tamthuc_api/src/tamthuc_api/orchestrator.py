from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from tamthuc_api.clients.core import CoreClient, StubCoreClient
from tamthuc_api.clients.engine import EngineClient, StubEngineClient
from tamthuc_api.clients.rag import RagClient, StubRagClient
from tamthuc_api.clients.rule import RuleClient, StubRuleClient


@dataclass
class Orchestrator:
    core: CoreClient = field(default_factory=StubCoreClient)
    engine: EngineClient = field(default_factory=StubEngineClient)
    rule: RuleClient = field(default_factory=StubRuleClient)
    rag: RagClient = field(default_factory=StubRagClient)
    call_log: list[str] = field(default_factory=list)

    def calculate(
        self, system: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        # nine-step simplified: auth assumed upstream
        self.call_log.append("core")
        lich = self.core.tinh_lich_phap(body)
        self.call_log.append("engine")
        chart = self.engine.cast(system, lich)
        # gateway must not recompute chart — pass engine envelope through
        envelope = chart
        self.call_log.append("rule")
        patterns = self.rule.match(envelope)
        self.call_log.append("rag")
        interpretation = self.rag.interpret(envelope, patterns)
        disclosure = interpretation.get("ai_disclosure")
        return {
            "query_id": str(uuid4()),
            "charts": {system: envelope},
            "patterns": patterns,
            "interpretation": interpretation,
            "ai_disclosure": disclosure,
        }

    def calculate_all(self, body: dict[str, Any]) -> dict[str, Any]:
        systems = ["qimen", "liuren", "taiyi"]
        charts: dict[str, Any] = {}
        for s in systems:
            self.call_log.append("core")
            lich = self.core.tinh_lich_phap(body)
            self.call_log.append("engine")
            charts[s] = self.engine.cast(s, lich)
        # fuse interpretation on first chart
        first = next(iter(charts.values()))
        self.call_log.append("rule")
        patterns = self.rule.match(first)
        self.call_log.append("rag")
        interpretation = self.rag.interpret(first, patterns)
        return {
            "query_id": str(uuid4()),
            "charts": charts,
            "patterns": patterns,
            "interpretation": interpretation,
            "ai_disclosure": interpretation.get("ai_disclosure"),
        }
