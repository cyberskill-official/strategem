from fastapi import APIRouter

router = APIRouter(tags=["knowledge"])


@router.get("/knowledge/patterns")
def list_patterns() -> dict[str, list[object]]:
    return {"patterns": []}
