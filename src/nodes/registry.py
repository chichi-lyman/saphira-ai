# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
In-memory (and optionally persistent) registry of paired Saphira Nodes.

Pairing flow (OpenClaw-style):
1. Device connects with role=node and presents identity → PENDING
2. Operator (or Saphira CLI / API) approves → ONLINE
3. Gateway routes node.invoke commands only to approved nodes
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging
import time

from .base import Node, NodeStatus, NodeType, NodeCapability

logger = logging.getLogger("SaphiraNodes")


class NodeRegistry:
    """Central registry for all companion nodes."""

    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._by_name: Dict[str, str] = {}  # name → id

    # ------------------------------------------------------------------
    # Registration & pairing
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        node_type: str | NodeType = NodeType.HEADLESS,
        host: Optional[str] = None,
        platform: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_approve: bool = False,
    ) -> Node:
        """Register a new node (or re-register an existing name)."""
        if isinstance(node_type, str):
            node_type = NodeType(node_type)

        caps = [NodeCapability(c) for c in (capabilities or [])] if capabilities else None

        # Re-register by name → update existing
        if name in self._by_name:
            existing = self._nodes[self._by_name[name]]
            existing.node_type = node_type
            existing.host = host or existing.host
            existing.platform = platform or existing.platform
            if caps:
                existing.capabilities = caps
            if metadata:
                existing.metadata.update(metadata)
            existing.touch()
            if auto_approve and existing.status == NodeStatus.PENDING:
                existing.approve()
            logger.info("Node re-registered: %s (%s)", existing.id, name)
            return existing

        node = Node(
            name=name,
            node_type=node_type,
            host=host,
            platform=platform,
            capabilities=caps or [],
            metadata=metadata or {},
        )
        if auto_approve:
            node.approve()
        else:
            node.status = NodeStatus.PENDING

        self._nodes[node.id] = node
        self._by_name[name] = node.id
        logger.info("Node registered: %s (%s) status=%s", node.id, name, node.status.value)
        return node

    def approve(self, id_or_name: str) -> Optional[Node]:
        node = self.get(id_or_name)
        if not node:
            return None
        node.approve()
        logger.info("Node approved: %s (%s)", node.id, node.name)
        return node

    def reject(self, id_or_name: str) -> Optional[Node]:
        node = self.get(id_or_name)
        if not node:
            return None
        node.reject()
        logger.info("Node rejected: %s (%s)", node.id, node.name)
        return node

    def remove(self, id_or_name: str) -> bool:
        node = self.get(id_or_name)
        if not node:
            return False
        del self._nodes[node.id]
        self._by_name.pop(node.name, None)
        return True

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, id_or_name: str) -> Optional[Node]:
        if id_or_name in self._nodes:
            return self._nodes[id_or_name]
        if id_or_name in self._by_name:
            return self._nodes[self._by_name[id_or_name]]
        # Fuzzy: match by host/ip fragment
        for n in self._nodes.values():
            if n.host and id_or_name in (n.host or ""):
                return n
        return None

    def list(
        self,
        status: Optional[str] = None,
        node_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status.value == status]
        if node_type:
            nodes = [n for n in nodes if n.node_type.value == node_type]
        return [n.to_dict() for n in nodes]

    def online(self) -> List[Node]:
        return [n for n in self._nodes.values() if n.status == NodeStatus.ONLINE]

    def find_by_capability(self, command: str) -> List[Node]:
        """Return online nodes that can handle the given command."""
        return [n for n in self.online() if n.has_capability(command)]

    def status_summary(self) -> Dict[str, Any]:
        counts = {s.value: 0 for s in NodeStatus}
        for n in self._nodes.values():
            counts[n.status.value] += 1
        return {
            "total": len(self._nodes),
            "by_status": counts,
            "online_ids": [n.id for n in self.online()],
            "owner": "Chelsea Megan Woods",
        }


# Singleton used by FastAPI and orchestrator
node_registry = NodeRegistry()
