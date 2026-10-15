# © 2026 Chelsea Megan Woods
# Lean TaskGraph — cycle detect, depth bound, no bloat.

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid
import time

class Status(str, Enum):
    PENDING = "P"
    READY = "R"
    RUN = "X"
    OK = "OK"
    FAIL = "F"

@dataclass
class Node:
    id: str
    capability: str
    agent_key: str
    payload: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    status: Status = Status.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 2
    timeout_s: float = 30.0
    isolation_token: str = field(default_factory=lambda: str(uuid.uuid4()))
    t0: float = 0.0

class TaskGraph:
    __slots__ = ("graph_id", "root", "tenant", "nodes", "edges", "done", "failed", "max_nodes")

    def __init__(self, root: str, tenant: str = "default", max_nodes: int = 48):
        self.graph_id = str(uuid.uuid4())
        self.root = root
        self.tenant = tenant
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Set[str]] = {}
        self.done: Set[str] = set()
        self.failed: Set[str] = set()
        self.max_nodes = max_nodes

    def add(self, n: Node) -> None:
        if len(self.nodes) >= self.max_nodes:
            raise RuntimeError("node limit")
        self.nodes[n.id] = n
        for d in n.depends_on:
            self.edges.setdefault(d, set()).add(n.id)

    def ready(self) -> List[Node]:
        out = []
        for n in self.nodes.values():
            if n.status == Status.PENDING and all(d in self.done for d in n.depends_on):
                n.status = Status.READY
                out.append(n)
        return out

    def has_cycle(self) -> bool:
        indeg = {i: len(n.depends_on) for i, n in self.nodes.items()}
        q = [i for i, d in indeg.items() if d == 0]
        seen = 0
        while q:
            u = q.pop()
            seen += 1
            for v in self.edges.get(u, ()):
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        return seen != len(self.nodes)

    def mark_ok(self, nid: str, result: Dict[str, Any]) -> None:
        n = self.nodes[nid]
        n.status = Status.OK
        n.result = result
        self.done.add(nid)

    def mark_fail(self, nid: str, err: str) -> None:
        n = self.nodes[nid]
        n.attempts += 1
        n.error = err
        if n.attempts >= n.max_attempts:
            n.status = Status.FAIL
            self.failed.add(nid)
        else:
            n.status = Status.PENDING
