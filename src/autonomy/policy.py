"""Risk-aware autonomy policy for real-world actions."""
from __future__ import annotations

import re

from src.orchestration.task import AutonomyDecision, Task


class AutonomyPolicy:
    """Conservative-by-default policy with explicit risk classification."""

    HIGH_RISK = (
        "transfer", "wire", "withdraw", "sign contract", "legal agreement",
        "delete production", "drop database", "rotate production", "buy",
    )
    EXTERNAL_COMMITMENT = (
        "send", "publish", "post", "reply", "contact", "email", "message",
        "merge", "deploy production", "create order", "purchase", "pay",
    )
    REVERSIBLE = (
        "research", "draft", "analyze", "summarize", "organize", "test",
        "inspect", "plan", "compare", "generate", "prepare",
    )

    def classify(self, task: Task) -> AutonomyDecision:
        text = re.sub(r"\s+", " ", task.objective.lower())
        high = next((term for term in self.HIGH_RISK if term in text), None)
        if high:
            return AutonomyDecision("approval_required", True, f"High-risk action: {high}", "high")
        external = next((term for term in self.EXTERNAL_COMMITMENT if term in text), None)
        if external:
            return AutonomyDecision("approval_required", True, f"External commitment: {external}", "medium")
        return AutonomyDecision("autonomous", False, None, "low")
