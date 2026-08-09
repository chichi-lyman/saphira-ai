"""Capability registry for invisible background workers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .task import Task


@dataclass(frozen=True)
class AgentSpec:
    name: str
    capabilities: frozenset[str]
    priority: int = 100
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRegistry:
    agents: dict[str, AgentSpec] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.agents:
            self.register(AgentSpec("planner_agent", frozenset({"reasoning"}), 10, "Planning and decomposition"))
            self.register(AgentSpec("research_agent", frozenset({"research"}), 20, "Research and analysis"))
            self.register(AgentSpec("developer_agent", frozenset({"development"}), 20, "Code and engineering"))
            self.register(AgentSpec("content_agent", frozenset({"content"}), 30, "Content production"))
            self.register(AgentSpec("commerce_agent", frozenset({"commerce"}), 30, "Commerce operations"))
            self.register(AgentSpec("communications_agent", frozenset({"communications"}), 30, "External communications"))
            self.register(AgentSpec("scheduling_agent", frozenset({"scheduling"}), 30, "Calendar and scheduling"))
            self.register(AgentSpec("operations_agent", frozenset({"operations"}), 30, "Business operations"))
            self.register(AgentSpec("qa_agent", frozenset({"quality"}), 10, "Verification and quality control"))

    def register(self, agent: AgentSpec) -> None:
        self.agents[agent.name] = agent

    def route(self, task: Task) -> list[str]:
        assigned: list[str] = []
        for step in task.plan:
            candidates = [a for a in self.agents.values() if step["capability"] in a.capabilities]
            candidates.sort(key=lambda a: a.priority)
            if candidates:
                step["agent"] = candidates[0].name
                if candidates[0].name not in assigned:
                    assigned.append(candidates[0].name)
        task.assigned_agents = assigned
        task.emit("agents_routed", agents=assigned)
        return assigned
