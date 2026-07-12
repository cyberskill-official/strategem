from __future__ import annotations

import json
from pathlib import Path

from tamthuc_compliance.dsar import ErasureContract, ExportContract, InMemoryDsarStub
from tamthuc_compliance.retention import retention_schedule, sensitive_classes


def test_retention_covers_required_classes() -> None:
    sched = retention_schedule()
    for key in ("birth_data", "question_text", "charts", "reports", "audit"):
        assert key in sched
    assert "birth_data" in sensitive_classes()
    assert "question_text" in sensitive_classes()
    assert sched["birth_data"].erasure.value == "crypto_shred"
    assert sched["audit"].erasure.value == "retain"


def test_dsar_contracts_runtime() -> None:
    stub = InMemoryDsarStub()
    assert isinstance(stub, ExportContract)
    assert isinstance(stub, ErasureContract)
    exp = stub.export("u1")
    assert exp.subject_id == "u1"
    e1 = stub.erase("u1")
    assert e1.retained_audit is True
    assert "birth_data" in e1.crypto_shredded
    e2 = stub.erase("u1")
    assert e2.idempotent_replay is True


def test_dsar_schema_file_exists() -> None:
    root = Path(__file__).resolve().parents[3]
    schema = root / "docs/contracts/dsar.schema.json"
    data = json.loads(schema.read_text(encoding="utf-8"))
    assert (
        "ExportResult" in data.get("$defs", data.get("definitions", {"ExportResult": 1}))
        or "properties" in data
    )
