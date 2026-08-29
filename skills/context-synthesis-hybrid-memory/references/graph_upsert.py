# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Graph upsert logic for UnifiedMemoryNode relations.

from __future__ import annotations
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

class GraphStore:
    """
    In-memory reference implementation of graph upsert and query.
    Swap the internal dict for Neo4j, Amazon Neptune, or another graph backend.
    """

    def __init__(self):
        # key = "subject:predicate:object" -> relation dict + metadata
        self._edges: Dict[str, Dict[str, Any]] = {}

    def _edge_key(self, subject: str, predicate: str, object_: str) -> str:
        return f"{subject}:{predicate}:{object_}"

    def upsert_relation(
        self,
        subject: str,
        predicate: str,
        object_: str,
        confidence_score: float,
        source_memory_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not 0.0 <= confidence_score <= 1.0:
            raise ValueError("confidence_score must be between 0 and 1")

        key = self._edge_key(subject, predicate, object_)
        existing = self._edges.get(key)

        if existing is None or confidence_score >= existing["confidence_score"]:
            record = {
                "subject": subject,
                "predicate": predicate,
                "object": object_,
                "confidence_score": confidence_score,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "source_memory_id": source_memory_id,
            }
            self._edges[key] = record
            return record

        return existing  # keep higher-confidence version

    def upsert_from_memory_node(self, memory_node: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        memory_id = memory_node.get("memory_id")
        for rel in memory_node.get("graph_relations", []):
            results.append(
                self.upsert_relation(
                    subject=rel["subject"],
                    predicate=rel["predicate"],
                    object_=rel["object"],
                    confidence_score=rel["confidence_score"],
                    source_memory_id=memory_id,
                )
            )
        return results

    def query_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        return [e for e in self._edges.values() if e["subject"] == subject]

    def query_by_predicate(self, predicate: str) -> List[Dict[str, Any]]:
        return [e for e in self._edges.values() if e["predicate"] == predicate]
