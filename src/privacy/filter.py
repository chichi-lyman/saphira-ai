"""Zero-egress privacy filter — redact PII and secrets before outbound I/O.

Keeps Saphira aligned with the 10/10 local-ownership privacy pillar.
Does not claim compliance certification; it enforces a practical sanitize boundary.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Common secret / PII patterns (conservative)
_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("api_key", re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})"), "[REDACTED_SECRET]"),
    ("bearer", re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]+"), "Bearer [REDACTED]"),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    ("phone", re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"), "[REDACTED_PHONE]"),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    ("cc", re.compile(r"\b(?:\d[ -]*?){13,19}\b"), "[REDACTED_CARD]"),
)


@dataclass
class RedactionResult:
    text: str
    redacted: bool
    categories: list[str] = field(default_factory=list)
    zero_egress: bool = True


class PrivacyFilter:
    """Sanitize outbound text and structured payloads."""

    def sanitize_text(self, text: str) -> RedactionResult:
        if not text:
            return RedactionResult(text="", redacted=False, categories=[])
        out = text
        categories: list[str] = []
        for name, pattern, repl in _PATTERNS:
            if pattern.search(out):
                out = pattern.sub(repl, out)
                categories.append(name)
        return RedactionResult(
            text=out,
            redacted=bool(categories),
            categories=categories,
            zero_egress=True,
        )

    def sanitize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Deep-copy style sanitize for string leaves."""

        def walk(value: Any) -> Any:
            if isinstance(value, str):
                return self.sanitize_text(value).text
            if isinstance(value, list):
                return [walk(v) for v in value]
            if isinstance(value, dict):
                return {k: walk(v) for k, v in value.items()}
            return value

        return walk(payload)

    def allow_egress(self, text: str) -> tuple[bool, RedactionResult]:
        """Return (ok_to_send, sanitized). Always returns sanitized form."""
        result = self.sanitize_text(text)
        return True, result
