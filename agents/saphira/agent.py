# Copyright © 2026 Chelsea Megan Woods
from pydantic import BaseModel, Field


class SaphiraAgent:
    """Only user-facing surface."""

    name = "saphira"
    default_policy = "ALLOW"

    def receive(self, utterance: str) -> dict:
        return {"agent": self.name, "intent": utterance, "route": "pipeline"}
