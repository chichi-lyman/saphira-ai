"""Active validator inspired by docs/HUMAN_LOGIC_RULEBOOK.md.

Fast gates before user-visible COMMIT. Not a full theorem prover.
Copyright © 2026 Chelsea Megan Woods
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LogicVerdict:
    ok: bool
    reasons: list[str]


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

    low = text.lower()
    if "cannot be done" in low and "successfully completed" in low:
        reasons.append("Potential contradiction: cannot-be-done vs successfully-completed")

    if instr and len(instr) > 20:
        if any(w in instr.lower() for w in ("list", "steps", "bullet")) and not any(
            m in text for m in ("-", "*", "1.", "2.")
        ):
            reasons.append("Instruction suggested structured list; output has no list markers")

    if metadata and metadata.get("loop_count", 0) >= 10:
        reasons.append("Loop count ≥ 10 — drift risk; abort recommended")

    return LogicVerdict(ok=len(reasons) == 0, reasons=reasons)
