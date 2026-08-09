"""Classify actions before Saphira delegates them to real-world tools."""

from __future__ import annotations

from src.orchestration.task import AutonomyDecision, Task


class AutonomyPolicy:
    """Conservative default policy for autonomous execution.

    Research, drafting, analysis, organization, testing, and other reversible
    work can proceed automatically. External commitments, financial actions,
    destructive operations, and irreversible changes require approval.
    """

    APPROVAL_TERMS = (
        "send", "publish", "purchase", "buy", "pay", "transfer", "delete",
        "remove", "sign", "merge to production", "deploy production",
    )

    def classify(self, task: Task) -> AutonomyDecision:
        text = task.objective.lower()
        restricted = [term for term in self.APPROVAL_TERMS if term in text]
        if restricted:
            return AutonomyDecision(
                level="approval_required",
                requires_approval=True,
                reason=f"Restricted action detected: {restricted[0]}",
            )
        return AutonomyDecision(level="autonomous", requires_approval=False)
