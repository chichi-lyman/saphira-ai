# Copyright © 2026 Chelsea Megan Woods
class NovaReignAgent:
    name = "novareign"
    default_policy = "ALLOW"

    def plan(self, goal: str) -> dict:
        return {
            "agent": self.name,
            "goal": goal,
            "dispatch": ["instinct", "apex", "scholar"],
        }
