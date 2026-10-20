"""Deterministic output checks before Saphira's user-visible commit boundary.

This is a lightweight structural validator, not a theorem prover or a guarantee
of factual correctness. Call require_valid_specialist_output before committing
specialist output to user-visible state.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class LogicVerdict:
    ok: bool
    reasons: list[str]


class InvalidSpecialistOutput(ValueError):
    """Raised when specialist output fails the pre-commit validation gate."""


_REPEAT_PATTERN = re.compile(r"(\S.{0,80}?)\1{3,}", re.IGNORECASE | re.DOTALL)
_CHAR_RUN_PATTERN = re.compile(r"(.)\1{11,}", re.DOTALL)


def validate_specialist_output(
    *,
    user_instruction: str,
    specialist_output: str,
    metadata: dict[str, Any] | None = None,
) -> LogicVerdict:
    reasons: list[str] = []
    text = (specialist_output or "").strip()
    instr = (user_instruction or "").strip()

    if not text:
        return LogicVerdict(False, ["Empty output violates usefulness"])

    if len(text) < 3:
        reasons.append("Output too short to be a complete response")

    if _CHAR_RUN_PATTERN.search(text) or _REPEAT_PATTERN.search(text):
        reasons.append("Repeated character or phrase loop detected")

    low = text.lower()
    if "assert false" in low:
        reasons.append("Explicit false assertion marker detected")
    if "cannot be done" in low and "successfully completed" in low:
        reasons.append("Potential contradiction: cannot-be-done vs successfully-completed")
    if len(text) < 100 and "is true" in low and "is false" in low:
        reasons.append("Potential contradiction: both true and false claims in short output")

    if instr and len(instr) > 20:
        if any(w in instr.lower() for w in ("list", "steps", "bullet")) and not any(
            m in text for m in ("-", "*", "1.", "2.", "•")
        ):
            reasons.append("Instruction suggested structured list; output has no list markers")

    if metadata and metadata.get("loop_count", 0) >= 10:
        reasons.append("Loop count ≥ 10 — drift risk; abort recommended")

    return LogicVerdict(ok=not reasons, reasons=reasons)


def require_valid_specialist_output(
    *,
    user_instruction: str,
    specialist_output: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Pre-commit gate: return the validated text or raise; never silently commit invalid text."""
    verdict = validate_specialist_output(
        user_instruction=user_instruction,
        specialist_output=specialist_output,
        metadata=metadata,
    )
    if not verdict.ok:
        raise InvalidSpecialistOutput("; ".join(verdict.reasons))
    return specialist_output.strip()
