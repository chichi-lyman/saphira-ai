# Copyright © 2026 Chelsea Megan Woods
class AgentTwo:
    name = "agent_two"
    default_policy = "REQUIRE_APPROVAL"

    def gate(self, action: dict) -> dict:
        return {"agent": self.name, "decision": "clear", "action": action}
