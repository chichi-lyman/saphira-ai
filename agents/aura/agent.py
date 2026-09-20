# Copyright © 2026 Chelsea Megan Woods
class AuraAgent:
    name = "aura"
    default_policy = "ALLOW"

    def perceive(self, payload: dict) -> dict:
        return {"agent": self.name, "perception": payload, "status": "ok"}
