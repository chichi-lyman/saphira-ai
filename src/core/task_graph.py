# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
#
# Elite TaskGraph — dependency-gated, cycle-safe, depth-limited graph for multi-agent work.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid
from datetime import datetime, timezone


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NEEDS_APPROVAL = "needs_approval"
    BLOCKED = "blocked"


@dataclass
class TaskNode:
    id: str
    capability: str
    agent_key: str
    payload: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    timeout_s: float = 60.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    isolation_token: str = field(default_factory=lambda: str(uuid.uuid4()))


class TaskGraph:
    """
    Fail-safe task graph used by EliteRouter.
    Hard limits prevent infinite loops and runaway agent chatter.
    """

    def __init__(self, root_intent: str, tenant_id: str = "default"):
        self.graph_id = str(uuid.uuid4())
        self.root_intent = root_intent
        self.tenant_id = tenant_id
        self.nodes: Dict[str, TaskNode] = {}
        self.edges: Dict[str, Set[str]] = {}
        self.completed: Set[str] = set()
        self.failed: Set[str] = set()
        self.max_depth = 12
        self.max_nodes = 64

    def add(self, node: TaskNode) -> None:
        if len(self.nodes) >= self.max_nodes:
            raise RuntimeError("TaskGraph node limit exceeded (max 64)")
        self.nodes[node.id] = node
        for dep in node.depends_on:
            self.edges.setdefault(dep, set()).add(node.id)

    def ready_wave(self) -> List[TaskNode]:
        ready: List[TaskNode] = []
        for n in self.nodes.values():
            if n.status != TaskStatus.PENDING:
                continue
            if all(d in self.completed for d in n.depends_on):
                n.status = TaskStatus.READY
                ready.append(n)
        return ready

    def has_cycle(self) -> bool:
        in_degree = {nid: len(n.depends_on) for nid, n in self.nodes.items()}
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited = 0
        while queue:
            u = queue.pop(0)
            visited += 1
            for v in self.edges.get(u, set()):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        return visited != len(self.nodes)

    def mark_done(self, node_id: str, result: Dict[str, Any]) -> None:
        n = self.nodes[node_id]
        n.status = TaskStatus.SUCCESS
        n.result = result
        n.finished_at = datetime.now(timezone.utc).isoformat()
        self.completed.add(node_id)

    def mark_failed(self, node_id: str, error: str) -> None:
        n = self.nodes[node_id]
        n.attempts += 1
        n.error = error
        if n.attempts >= n.max_attempts:
            n.status = TaskStatus.FAILED
            self.failed.add(node_id)
        else:
            n.status = TaskStatus.PENDING
