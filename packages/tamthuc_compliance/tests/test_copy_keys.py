import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KEYS = ROOT / "docs/legal/copy-deck/copy-keys.yaml"
DECK = ROOT / "docs/legal"


def test_copy_keys_exist() -> None:
    text = KEYS.read_text(encoding="utf-8")
    assert "disclaimer.product.vi" in text
    assert "ai.limits.en" in text
    assert "counsel_review_required: true" in text


def test_forbidden_lexicon_absent_from_deck() -> None:
    bad = re.compile(r"(?i)you will definitely|chắc chắn sẽ|cure cancer|guaranteed profit")
    for p in (DECK / "copy-deck").rglob("*.md"):
        body = p.read_text(encoding="utf-8")
        assert not bad.search(body), p
