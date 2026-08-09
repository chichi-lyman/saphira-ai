"""Capability registry for Saphira's invisible background workforce."""
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
        if self.agents:
            return
        defaults = (
            ("planner_agent", {"reasoning"}, 10, "Planning and decomposition"),
            ("research_agent", {"research", "web"}, 20, "Research, retrieval and grounding"),
            ("developer_agent", {"development", "system"}, 20, "Code, engineering and permitted system workflows"),
            ("content_agent", {"content"}, 30, "Content production"),
            ("commerce_agent", {"commerce"}, 30, "Commerce operations"),
            ("communications_agent", {"communications"}, 30, "External communications"),
            ("scheduling_agent", {"scheduling", "proactive"}, 30, "Calendar and proactive scheduling"),
            ("operations_agent", {"operations"}, 30, "Business operations"),
            ("voice_agent", {"voice"}, 20, "Speech input/output"),
            ("vision_agent", {"vision"}, 20, "Visual and screen perception"),
            ("stem_agent", {"stem"}, 20, "Deterministic math/science/engineering"),
            ("cad_agent", {"cad"}, 30, "Parametric CAD/3D generation"),
            ("system_agent", {"system"}, 30, "Explicitly scoped OS/device control"),
            ("iot_agent", {"iot"}, 30, "Smart environment integrations"),
            ("memory_agent", {"memory"}, 10, "Long-term memory and context"),
            ("qa_agent", {"quality"}, 10, "Verification and quality control"),
        )
        for name, capabilities, priority, description in defaults:
            self.register(AgentSpec(name, frozenset(capabilities), priority, description))

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
