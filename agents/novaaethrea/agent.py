# Copyright © 2026 Chelsea Megan Woods
class NovaAethreaAgent:
    name = "novaaethrea"
    default_policy = "ALLOW"

    def remember(self, key: str, value: dict) -> dict:
        return {"agent": self.name, "stored": key, "value": value}
