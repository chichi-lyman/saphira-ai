# Copyright © 2026 Chelsea Megan Woods
class LexisAgent:
    name = "lexis"
    default_policy = "REQUIRE_APPROVAL"

    def review(self, document: str) -> dict:
        return {
            "agent": self.name,
            "document_preview": document[:200],
            "policy": "REQUIRE_APPROVAL",
            "note": "Not formal legal advice",
        }
