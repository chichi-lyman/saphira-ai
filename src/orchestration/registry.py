"""Capability-based routing from task steps to background workers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .task import Task


@dataclass
class AgentRegistry:
    capabilities: dict[str, str] = field(default_factory=lambda: {
        "research": "research_agent",
        "development": "developer_agent",
        "content": "content_agent",
        "commerce": "commerce_agent",
        "communications": "communications_agent",
        "quality": "qa_agent",
        "reasoning": "planner_agent",
    })

    def route(self, task: Task) -> list[str]:
        assigned: list[str] = []
        for step in task.plan:
            agent = self.capabilities.get(step["capability"])
            if agent and agent not in assigned:
                assigned.append(agent)
        return assigned
