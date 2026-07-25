from __future__ import annotations

from pathlib import Path

from tamthuc_rag.fuse import RankedHit

PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_VERSION = "rag-003@1"


def build_prompt(laso: dict[str, object], chunks: list[RankedHit], persona: str) -> str:
    sys = (PROMPT_DIR / "system.md").read_text(encoding="utf-8")
    body = (PROMPT_DIR / f"{persona}.md").read_text(encoding="utf-8")
    cite_lines: list[str] = []
    for c in chunks:
        layers = " | ".join(f"{k}={v}" for k, v in c.layers.items() if v)
        cite_lines.append(f"- {c.citation_id}: {layers or list(c.layers.values())[:1]}")
    cites = "\n".join(cite_lines)
    return f"{sys}\n\n{body}\n\n## La so (read-only)\n{laso}\n\n## Retrieved sources\n{cites}\n"
