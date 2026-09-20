# Copyright © 2026 Chelsea Megan Woods
class InstinctAgent:
    name = "instinct"
    default_policy = "ALLOW"

    def content_brief(self, topic: str, intensity: str = "raw") -> dict:
        return {
            "agent": self.name,
            "topic": topic,
            "intensity": intensity,
            "can_publish": True,
            "policy": "ALLOW",
            "allow_rage_jealousy_hooks": True,
        }
