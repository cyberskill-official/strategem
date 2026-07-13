"""EDU product routes — COV-014 grade + COV-015 library + COV-016 onboarding."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from tamthuc_api.errors import error_envelope

router = APIRouter(tags=["edu"])


class GradeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    system: str = "qimen"
    student_seat_ids: list[str] = Field(default_factory=list)
    """Student answers for deterministic seats (pattern ids or palace labels)."""
    engine_envelope: dict[str, Any] = Field(default_factory=dict)
    """Engine la so envelope — grader reads only deterministic slices."""


@router.post("/edu/practice/grade", response_model=None)
def grade_practice(body: GradeBody) -> dict[str, Any] | JSONResponse:
    """COV-014: grade seat/pattern ids against engine cach_cuc only (no interpretation)."""
    try:
        from tamthuc_edu.grade import grade_chart_practice
    except ImportError:
        return JSONResponse(
            status_code=501,
            content=error_envelope("NOT_IMPLEMENTED", "tamthuc_edu not installed"),
        )

    # CellDiff-style feedback for wrong seats
    expected: list[str] = []
    raw = body.engine_envelope.get("cach_cuc") or []
    if isinstance(raw, list):
        for c in raw:
            if isinstance(c, dict) and c.get("id"):
                expected.append(str(c["id"]))
            elif isinstance(c, str):
                expected.append(c)

    result = grade_chart_practice(body.student_seat_ids, body.engine_envelope)
    exp_set = set(result.expected_ids)
    stu_set = set(result.student_ids)
    missing = sorted(exp_set - stu_set)
    extra = sorted(stu_set - exp_set)
    cell_diffs = [
        {"kind": "missing", "id": mid, "message": f"Thiếu chỗ / mã: {mid}"} for mid in missing
    ] + [{"kind": "extra", "id": eid, "message": f"Thừa chỗ / mã: {eid}"} for eid in extra]

    return {
        "passed": result.passed,
        "score": result.score,
        "expected_ids": result.expected_ids,
        "student_ids": result.student_ids,
        "feedback": result.feedback,
        "cell_diffs": cell_diffs,
        "graded_slice": "cach_cuc_ids_only",
        "note": "Deterministic seats only — interpretation meaning is never graded.",
    }


@router.get("/edu/library")
def classical_library(
    q: str = Query(default=""),
    lang: str = Query(default="all"),
) -> dict[str, Any]:
    """COV-015: bilingual classical library (Han + bạch thoại + dich)."""
    try:
        from tamthuc_edu.library import ClassicalLibrary, LibraryEntry
    except ImportError:
        return {"entries": [], "total": 0}

    # Seed minimal educational entries + KB pattern names when available
    seed: list[Any] = [
        LibraryEntry(
            unit_id="yba_1",
            title="Yên Ba · mẫu",
            han="青龍返首",
            bach_thoai="Thanh Long quay đầu — khí mở, vẫn cần bối cảnh thực.",
            dich="Azure Dragon turns head — an opening signal, not a verdict.",
            system="qimen",
        ),
        LibraryEntry(
            unit_id="ln_nguyen_thu",
            title="Nguyên Thủ",
            han="元首",
            bach_thoai="Khóa thể Nguyên Thủ — đọc chỗ, không kết án.",
            dich="Chief lesson form — seat reading only.",
            system="liuren",
        ),
        LibraryEntry(
            unit_id="tat_yem",
            title="Yểm",
            han="掩",
            bach_thoai="Thái Ất yểm — vị trí tương đối, không tuyên bố thắng thua.",
            dich="Cover relation — positional fact, no victory claim.",
            system="taiyi",
        ),
    ]
    try:
        from tamthuc_kb.seed.loader import load_all_patterns

        for r in load_all_patterns()[:80]:
            if not isinstance(r, dict):
                continue
            han = str(r.get("name_han") or r.get("name") or "")
            seed.append(
                LibraryEntry(
                    unit_id=str(r.get("id") or han),
                    title=str(r.get("name") or han),
                    han=han,
                    bach_thoai=str(r.get("meaning_modern") or r.get("meaning_classical") or ""),
                    dich=str(r.get("meaning_classical") or r.get("meaning_modern") or ""),
                    system=str(r.get("system") or "all"),
                )
            )
    except Exception:
        pass

    lib = ClassicalLibrary(entries=seed)
    hits = lib.search(q, lang=lang) if q else list(lib.entries)
    # never drop Han layer in response shape
    out = []
    for e in hits[:200]:
        out.append(
            {
                "unit_id": e.unit_id,
                "title": e.title,
                "han": e.han or e.title,
                "bach_thoai": e.bach_thoai,
                "dich": e.dich,
                "system": e.system,
                "layers": {
                    "han": e.han or e.title,
                    "bach_thoai": e.bach_thoai,
                    "dich": e.dich,
                },
            }
        )
    return {"entries": out, "total": len(out), "source": "edu_library+kb_seed"}


@router.get("/edu/onboarding")
def onboarding() -> dict[str, Any]:
    """COV-016: first-run steps (skippable client-side)."""
    try:
        from tamthuc_edu.onboarding import help_topics, onboarding_path
    except ImportError:
        return {"steps": [], "help": []}

    # VI-first product copy (plain language for AIDisclosure + HumanReview)
    steps = [
        {
            "id": "welcome",
            "title": "Chào mừng",
            "body": "Tam Thức Strategem hỗ trợ suy nghĩ và học hỏi — không bói toán chắc chắn.",
            "cta": "Tiếp",
        },
        {
            "id": "cast",
            "title": "Thử một lần",
            "body": "Nhập thời điểm và câu hỏi. Máy dựng ban đồ xác định — cùng đầu vào, cùng kết quả.",
            "cta": "Thử ngay",
            "href": "/cast",
        },
        {
            "id": "disclosure",
            "title": "Nhãn AI & duyệt người",
            "body": (
                "Khi có diễn giải mô hình, luôn có nhãn AIDisclosure (mô hình, trích dẫn). "
                "Các chủ đề nhạy cảm có thể qua HumanReview — tạm giữ cho đến khi người duyệt."
            ),
            "cta": "Hiểu rồi",
        },
        {
            "id": "decide",
            "title": "Bạn quyết định",
            "body": "Dùng khung chủ–khách để soi thế. Công cụ không ra lời kết thay bạn.",
            "cta": "Xong",
            "href": "/learn",
        },
    ]
    help_vi = [
        {
            "id": "disclaimer",
            "title": "Tuyên bố",
            "body": "Chỉ để suy nghĩ và học hỏi — không thay lời khuyên y tế, pháp lý, tài chính.",
            "tags": ["legal", "voice"],
        },
        {
            "id": "ai_disclosure",
            "title": "AIDisclosure là gì?",
            "body": "Nhãn cho biết có dùng mô hình không, phiên bản prompt, và các trích dẫn đã lấy.",
            "tags": ["ai", "trust"],
        },
        {
            "id": "human_review",
            "title": "HumanReview",
            "body": "Cổng người duyệt cho diễn giải rủi ro cao; có thể pending cho đến khi phê duyệt.",
            "tags": ["ai", "safety"],
        },
        {
            "id": "schools",
            "title": "Cờ trường phái",
            "body": "Cấu hình dưới Quản lý → Tuỳ chọn. Không có trường phái nào được gắn «đúng tuyệt đối».",
            "tags": ["settings"],
        },
        *[
            {"id": h["id"], "title": h["title"], "body": h["body"], "tags": []}
            for h in help_topics()
        ],
    ]
    # also expose package path for parity
    _ = onboarding_path
    return {"steps": steps, "help": help_vi}
