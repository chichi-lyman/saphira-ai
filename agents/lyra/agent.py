# Copyright © 2026 Chelsea Megan Woods
class LyraAgent:
    name = "lyra"
    default_policy = "REQUIRE_APPROVAL"

    def analyze(self, metrics: dict) -> dict:
        return {"agent": self.name, "metrics": metrics, "summary": "pending"}
