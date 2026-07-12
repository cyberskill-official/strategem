from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from tamthuc_rag.schema import Interpretation


class EthicsSeverity(StrEnum):
    high = "high"
    medium = "medium"
    low = "low"


@dataclass
class EthicsFinding:
    family: str
    severity: EthicsSeverity
    message: str


_LANG = re.compile(
    r"(?i)\b(you will definitely|chắc chắn sẽ|diagnose|prescribe|invest now|sue them|"
    r"cure|guaranteed)\b"
)
_SCHOOL = re.compile(r"(?i)\b(only correct school|duy nhất đúng|all other schools wrong)\b")


def check_ethics(interp: Interpretation) -> list[EthicsFinding]:
    findings: list[EthicsFinding] = []
    text = " ".join(
        [
            interp.beginner,
            interp.expert,
            " ".join(str(r.get("text", "")) for r in interp.recommendations),
        ]
    )
    if _LANG.search(text):
        findings.append(EthicsFinding("language", EthicsSeverity.high, "forbidden framing lexicon"))
    if _SCHOOL.search(text):
        findings.append(
            EthicsFinding("school_fairness", EthicsSeverity.medium, "absolutist school claim")
        )
    for card in interp.citations:
        if not card.citation_id:
            findings.append(
                EthicsFinding("attribution", EthicsSeverity.high, "missing citation_id")
            )
        elif "han" not in card.layers and card.layers:
            # if layers present but no han when source may have han — medium
            pass
    for rec in interp.recommendations:
        if not rec.get("citations"):
            findings.append(
                EthicsFinding("attribution", EthicsSeverity.high, "uncited recommendation")
            )
    return findings


def policy_action(findings: list[EthicsFinding]) -> str:
    if any(f.severity == EthicsSeverity.high for f in findings):
        return "block"
    if any(f.severity == EthicsSeverity.medium for f in findings):
        return "human_review"
    return "allow"
