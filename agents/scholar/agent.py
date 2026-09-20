# Copyright © 2026 Chelsea Megan Woods
class ScholarAgent:
    name = "scholar"
    default_policy = "ALLOW"

    def playbook(self, topic: str) -> dict:
        return {
            "agent": self.name,
            "topic": topic,
            "steps": [
                "Frame the situation",
                "One action today",
                "Reflective question",
                "Close with agency",
            ],
        }
