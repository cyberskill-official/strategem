"""Follow-up chat answers grounded in a persisted cast (W6 / Grok UI 07).

Reuses the RAG retrieve + interpret path. Answers stay cited and MUST NOT invent
chart seat / stem numbers beyond what the stored envelope already contains.
Anti-destiny ethics framing is always attached.
"""

from __future__ import annotations

import re
from typing import Any

from tamthuc_api.clients.rag import LocalRagClient, RagClient, StubRagClient

_ETHICS_VI = (
    "Đây là gợi ý giáo dục di sản — không phải định mệnh, "
    "không thay lời khuyên y tế / pháp lý / tài chính."
)
_ETHICS_EN = (
    "Heritage-education reading only — not destiny, and not medical, legal, or financial advice."
)

# Questions that fish for numeric chart inventiveness.
_NUMBER_ASK = re.compile(
    r"(?i)("
    r"cung\s*\d+|palace\s*\d+|seat\s*(?:number|#)?\s*\d+|"
    r"(?:exact|chính\s*xác).{0,24}(?:số|number|stem|can|chi)|"
    r"(?:invent|bịa|đoán).{0,20}(?:số|number)|"
    r"how many|bao nhiêu cung"
    r")"
)


def _first_envelope(result: dict[str, Any]) -> dict[str, Any]:
    charts = result.get("charts") or {}
    if isinstance(charts, dict) and charts:
        first = next(iter(charts.values()))
        if isinstance(first, dict):
            return first
    return {}


def _patterns(result: dict[str, Any], envelope: dict[str, Any]) -> list[dict[str, Any]]:
    raw = result.get("patterns")
    if isinstance(raw, list) and raw:
        return [p for p in raw if isinstance(p, dict)]
    cc = envelope.get("cach_cuc")
    if isinstance(cc, list):
        return [p for p in cc if isinstance(p, dict)]
    return []


def _known_numbers(envelope: dict[str, Any], patterns: list[dict[str, Any]]) -> set[str]:
    """Seat / cung indices already present on the stored chart — never invent beyond these."""
    known: set[str] = set()
    for p in patterns:
        cung = p.get("cung")
        if cung is not None:
            known.add(str(cung))
    ban = envelope.get("ban")
    if isinstance(ban, dict):
        for key in ("dia_ban", "thien_ban", "cung"):
            val = ban.get(key)
            if isinstance(val, list):
                for i, _cell in enumerate(val):
                    known.add(str(i + 1 if i < 9 else i))
    return known


def _asks_to_invent_numbers(message: str, known: set[str]) -> bool:
    if not _NUMBER_ASK.search(message):
        return False
    # If they ask for a specific cung N that is not on the chart, refuse inventing it.
    for m in re.finditer(r"(?i)(?:cung|palace|seat)\s*(\d+)", message):
        if m.group(1) not in known:
            return True
    # Generic "invent numbers" / "exact stem count" without grounding → refuse fabrication.
    return bool(re.search(r"(?i)invent|bịa|đoán\s*số|make up", message))


def _citation_cards(interp: dict[str, Any]) -> list[dict[str, Any]]:
    cites = interp.get("citations") or []
    out: list[dict[str, Any]] = []
    if isinstance(cites, list):
        for c in cites:
            if isinstance(c, dict):
                out.append(c)
    return out


def _ethics_line(locale: str) -> str:
    return _ETHICS_VI if locale.lower().startswith("vi") else _ETHICS_EN


def _refuse_invented(
    *,
    message: str,
    locale: str,
    known: set[str],
) -> dict[str, Any]:
    ethics = _ethics_line(locale)
    if locale.lower().startswith("vi"):
        beginner = (
            "Mình không thể bịa số cung / can chi ngoài những gì đã có trên la số đã lưu. "
            f"Các vị trí đã ghi trên bàn: {', '.join(sorted(known)) or 'không có số cung lưu'}. "
            "Hãy hỏi về cách cục hoặc ý nghĩa đã trích dẫn thay vì yêu cầu số mới."
        )
    else:
        beginner = (
            "I will not invent palace or stem numbers beyond the stored chart. "
            f"Known seat indices on this cast: {', '.join(sorted(known)) or 'none recorded'}. "
            "Ask about cited patterns or classical meanings instead."
        )
    return {
        "query_id": None,
        "message": message,
        "answer": {
            "beginner": f"{beginner}\n\n{ethics}",
            "expert": beginner,
            "recommendations": [],
            "citations": [],
            "confidence": 0.0,
            "requires_human_review": False,
        },
        "ai_disclosure": {
            "is_ai_generated": True,
            "model": "follow-up-refuse",
            "prompt_version": "followup@1",
            "retrieved_citation_ids": [],
            "limits": ethics,
            "review_status": "not_required",
            "degraded": False,
            "mode_badge": "refuse-invent",
        },
        "refused": True,
        "refuse_reason": "chart_number_invention",
    }


def answer_follow_up(
    *,
    query_result: dict[str, Any],
    message: str,
    rag: RagClient | None = None,
    locale: str = "vi",
) -> dict[str, Any]:
    """Ground a follow-up turn on the persisted cast + RAG citations."""
    text = (message or "").strip()
    if not text:
        raise ValueError("message required")

    envelope = _first_envelope(query_result)
    patterns = _patterns(query_result, envelope)
    known = _known_numbers(envelope, patterns)
    qid = str(query_result.get("query_id") or "")

    if _asks_to_invent_numbers(text, known):
        out = _refuse_invented(message=text, locale=locale, known=known)
        out["query_id"] = qid
        return out

    client: RagClient = rag or LocalRagClient()
    env = dict(envelope)
    env["follow_up_question"] = text
    env.setdefault("dau_vao", {})
    if isinstance(env["dau_vao"], dict):
        env["dau_vao"] = {**env["dau_vao"], "follow_up": text}

    # D-REVIEW-001: do not expand on a parent cast still under review.
    parent_interp = query_result.get("interpretation") or {}
    if isinstance(parent_interp, dict):
        parent_status = str(
            (parent_interp.get("ai_disclosure") or {}).get("review_status")
            or parent_interp.get("review_status")
            or ""
        )
        if (
            parent_status in {"pending", "rejected"}
            or parent_interp.get("human_review_gate") == "pending"
        ):
            ethics = _ethics_line(locale)
            summary = (
                "Interpretation not released."
                if parent_status == "rejected"
                else "This interpretation is under human review."
            )
            return {
                "query_id": qid,
                "message": text,
                "answer": {
                    "beginner": f"{summary}\n\n{ethics}",
                    "expert": summary,
                    "recommendations": [],
                    "citations": [],
                    "confidence": float(parent_interp.get("confidence") or 0.0),
                    "requires_human_review": True,
                },
                "ai_disclosure": {
                    "is_ai_generated": True,
                    "model": "follow-up-withheld",
                    "prompt_version": "followup@1",
                    "retrieved_citation_ids": [],
                    "limits": ethics,
                    "review_status": parent_status or "pending",
                    "degraded": False,
                    "mode_badge": "review-pending",
                },
                "refused": True,
                "refuse_reason": "review_pending",
            }

    retrieved = client.retrieve(env, patterns)
    interp = client.interpret(env, patterns, retrieved=retrieved)
    if not isinstance(interp, dict):
        interp = {}

    ethics = _ethics_line(locale)
    interp_status = str(
        (interp.get("ai_disclosure") or {}).get("review_status")
        or interp.get("review_status")
        or ""
    )
    if interp_status in {"pending", "rejected"} or interp.get("human_review_gate") == "pending":
        summary = (
            "Interpretation not released."
            if interp_status == "rejected"
            else "This interpretation is under human review."
        )
        return {
            "query_id": qid,
            "message": text,
            "answer": {
                "beginner": f"{summary}\n\n{ethics}",
                "expert": summary,
                "recommendations": [],
                "citations": list(interp.get("citations") or []),
                "confidence": float(interp.get("confidence") or 0.0),
                "requires_human_review": True,
            },
            "ai_disclosure": {
                **dict(interp.get("ai_disclosure") or {}),
                "is_ai_generated": True,
                "model": (interp.get("ai_disclosure") or {}).get("model") or "follow-up-withheld",
                "prompt_version": "followup@1",
                "limits": ethics,
                "review_status": interp_status or "pending",
                "mode_badge": "review-pending",
            },
            "refused": True,
            "refuse_reason": "review_pending",
        }

    beginner = str(interp.get("beginner") or interp.get("summary") or "").strip()
    expert = str(interp.get("expert") or beginner).strip()
    if not beginner:
        names = [str(p.get("name") or p.get("id") or "") for p in patterns if p]
        names = [n for n in names if n][:3]
        if locale.lower().startswith("vi"):
            beginner = (
                f"Về câu hỏi «{text}»: dựa trên cách cục đã phát hiện"
                + (f" ({', '.join(names)})" if names else "")
                + " và các đoạn cổ điển đã truy xuất. "
                "Mình chỉ nêu ý nghĩa đã có trích dẫn — không thêm số liệu ngoài la số."
            )
        else:
            beginner = (
                f"On «{text}»: based on detected patterns"
                + (f" ({', '.join(names)})" if names else "")
                + " and retrieved classical passages. "
                "Only cited meanings — no chart numbers beyond the stored envelope."
            )
        expert = beginner

    # Address the follow-up explicitly when the model returned a generic reading.
    if text and text.lower() not in beginner.lower():
        prefix = (
            f"Về câu hỏi tiếp theo «{text}»: "
            if locale.lower().startswith("vi")
            else f"On your follow-up «{text}»: "
        )
        beginner = prefix + beginner
        expert = prefix + expert

    if ethics not in beginner:
        beginner = f"{beginner}\n\n{ethics}"
    if ethics not in expert:
        expert = f"{expert}\n\n{ethics}"

    disc = dict(interp.get("ai_disclosure") or {})
    disc.setdefault("is_ai_generated", True)
    disc.setdefault("model", disc.get("model") or "follow-up-rag")
    disc["prompt_version"] = "followup@1"
    disc["limits"] = ethics
    disc.setdefault("review_status", interp.get("review_status") or "not_required")
    cites = _citation_cards(interp)
    cite_ids = [
        str(c.get("citation_id")) for c in cites if isinstance(c, dict) and c.get("citation_id")
    ]
    if not cite_ids:
        cite_ids = [str(x) for x in (disc.get("retrieved_citation_ids") or [])]
    disc["retrieved_citation_ids"] = cite_ids

    # Stub clients still produce educational copy with at least stub citations.
    if isinstance(client, StubRagClient) and not cite_ids:
        disc["retrieved_citation_ids"] = ["yba_1"]
        cites = [
            {
                "citation_id": "yba_1",
                "layers": {"dich": "Stub classical unit for follow-up grounding."},
            }
        ]

    return {
        "query_id": qid,
        "message": text,
        "answer": {
            "beginner": beginner,
            "expert": expert,
            "recommendations": list(interp.get("recommendations") or []),
            "citations": cites,
            "confidence": float(interp.get("confidence") or 0.55),
            "requires_human_review": bool(interp.get("requires_human_review")),
        },
        "ai_disclosure": disc,
        "refused": False,
        "refuse_reason": None,
    }
