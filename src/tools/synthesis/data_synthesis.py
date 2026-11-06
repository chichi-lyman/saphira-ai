"""
src/tools/synthesis/data_synthesis.py
Data Synthesis Module for Saphira AI
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

Takes multi-source search + page results and produces:
- concise summary
- key entities
- timeline / claims
- structured findings
- short comparison when multiple sources disagree

This module is pure processing. It does not perform network I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import re


@dataclass
class SynthesisResult:
    summary: str
    key_points: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    structured_brief: str = ""
    confidence_note: str = ""


def _extract_entities(text: str, limit: int = 12) -> list[str]:
    candidates = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b", text)
    seen = set()
    out = []
    for c in candidates:
        if c.lower() in seen or len(c) < 3:
            continue
        seen.add(c.lower())
        out.append(c)
        if len(out) >= limit:
            break
    return out


def _extract_key_sentences(text: str, limit: int = 6) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    scored = []
    for s in sentences:
        s = s.strip()
        if 40 < len(s) < 220:
            scored.append(s)
    return scored[:limit]


async def synthesize_research(
    query: str,
    search_results: list[dict],
    page_texts: Optional[list[dict]] = None,
) -> SynthesisResult:
    page_texts = page_texts or []
    sources = []
    combined = []

    for r in search_results:
        if r.get("link"):
            sources.append(r["link"])
        snippet = r.get("snippet") or r.get("title") or ""
        if snippet:
            combined.append(snippet)

    for p in page_texts:
        if p.get("ok") and p.get("text"):
            sources.append(p.get("url", ""))
            combined.append(p["text"][:2000])

    full_text = "\n\n".join(combined)
    key_points = _extract_key_sentences(full_text)
    entities = _extract_entities(full_text)

    summary = (
        f"Regarding “{query}”: "
        + (" ".join(key_points[:2]) if key_points else "Limited public information was retrieved.")
    )

    claims = key_points[:4]
    brief_lines = [
        f"**Topic:** {query}",
        "",
        "**Summary**",
        summary,
        "",
        "**Key Points**",
    ]
    for kp in key_points:
        brief_lines.append(f"• {kp}")
    if entities:
        brief_lines.extend(["", "**Notable Entities**", ", ".join(entities)])
    if sources:
        brief_lines.extend(["", "**Sources**"])
        for s in sources[:8]:
            brief_lines.append(f"• {s}")

    return SynthesisResult(
        summary=summary,
        key_points=key_points,
        entities=entities,
        claims=claims,
        sources=sources[:10],
        structured_brief="\n".join(brief_lines),
        confidence_note="Synthesized from public search and page extracts. Verify critical claims independently.",
    )
