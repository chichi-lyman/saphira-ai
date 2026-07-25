# Dynamic Agent Factory with Full Registration
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any
from src.agents.boundary_coach import BoundaryCoachAgent
from src.agents.admin_resolver import AdminResolverAgent
from src.agents.relationship_agent import RelationshipAgent
from src.agents.lifestyle_orchestrator import LifestyleOrchestratorAgent

class DynamicAgentFactory:
    def __init__(self, router):
        self.router = router
        self.registry = {
            "boundary_coach": BoundaryCoachAgent(router),
            "admin_resolver": AdminResolverAgent(router),
            "relationship": RelationshipAgent(router),
            "lifestyle_orchestrator": LifestyleOrchestratorAgent(router),
        }

    async def spawn_agent(self, task_description: str, agent_name: str) -> Dict[str, Any]:
        # Prefer registered agents first
        if agent_name in self.registry:
            return {
                "status": "created",
                "agent_name": agent_name,
                "instance": self.registry[agent_name],
                "source": "registry"
            }
        
        # Fallback to dynamic generation (simplified)
        return {
            "status": "error",
            "message": f"Agent '{agent_name}' not found in registry and dynamic generation is disabled for safety."
        }

    def list_agents(self):
        return list(self.registry.keys())
