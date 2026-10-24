"""The Weaver — Contextual Cartographer & Synthesis Engine.

Copyright © 2026 Chelsea Megan Woods

Three-tier loop:
1. Graph-grounded parsing (semantic nodes)
2. Hybrid vector & topological RAG (cross-domain analogues)
3. Dynamic visualization specs (concept maps)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger("SaphiraWeaver")


class LevelShift(str, Enum):
    CHILD = "explain_to_8_year_old"
    GENERAL = "general_synthesis"
    POSTDOC = "postdoctoral_technical"
    AVANT_GARDE = "sci_fi_avant_garde"


@dataclass
class SemanticNode:
    id: str
    label: str
    kind: str  # entity | emotion | rule | domain | other
    domain: str | None = None
    weight: float = 1.0


@dataclass
class AnalogyBridge:
    source_node: str
    target_node: str
    structural_basis: str
    novelty: float
    grounded: bool = False
    note: str = "proposed bridge — not proven fact unless grounded"


@dataclass
class ConceptMap:
    id: str = field(default_factory=lambda: f"map_{uuid4().hex[:10]}")
    objective: str = ""
    nodes: list[SemanticNode] = field(default_factory=list)
    bridges: list[AnalogyBridge] = field(default_factory=list)
    level: LevelShift = LevelShift.GENERAL
    visualization: dict[str, Any] = field(default_factory=dict)


class WeaverEngine:
    """Parse → synthesize → visualize. Stub retrieval; adapters plug in later."""

    def parse(self, text: str) -> list[SemanticNode]:
        # Lightweight heuristic tokenization into nodes (production: LLM + KG)
        parts = [p.strip() for p in text.replace(",", " ").split() if len(p.strip()) > 2]
        seen: set[str] = set()
        nodes: list[SemanticNode] = []
        for i, part in enumerate(parts[:24]):
            key = part.lower()
            if key in seen:
                continue
            seen.add(key)
            nodes.append(
                SemanticNode(
                    id=f"n_{i}_{uuid4().hex[:4]}",
                    label=part,
                    kind="entity",
                    weight=1.0,
                )
            )
        if not nodes:
            nodes.append(
                SemanticNode(id=f"n_0_{uuid4().hex[:4]}", label=text[:80] or "idea", kind="entity")
            )
        return nodes

    def cross_synthesize(
        self,
        nodes: list[SemanticNode],
        domains: list[str] | None = None,
    ) -> list[AnalogyBridge]:
        bridges: list[AnalogyBridge] = []
        if len(nodes) >= 2:
            a, b = nodes[0], nodes[1]
            bridges.append(
                AnalogyBridge(
                    source_node=a.id,
                    target_node=b.id,
                    structural_basis=(
                        f"Structural analogy between '{a.label}' and '{b.label}'"
                        + (f" across {domains}" if domains else "")
                    ),
                    novelty=0.7,
                    grounded=False,
                )
            )
        for i in range(2, min(len(nodes), 6)):
            bridges.append(
                AnalogyBridge(
                    source_node=nodes[0].id,
                    target_node=nodes[i].id,
                    structural_basis=f"Secondary link from core idea to '{nodes[i].label}'",
                    novelty=0.4,
                    grounded=False,
                )
            )
        return bridges

    def level_shift_text(self, objective: str, level: LevelShift, bridges: list[AnalogyBridge]) -> str:
        bridge_blurb = "; ".join(b.structural_basis for b in bridges[:2]) or "emerging connections"
        if level == LevelShift.CHILD:
            return (
                f"Imagine your idea about '{objective}' like building blocks. "
                f"We found friendly bridges: {bridge_blurb}. "
                "Let's play with how those blocks fit together."
            )
        if level == LevelShift.POSTDOC:
            return (
                f"Technical synthesis for '{objective}'. "
                f"Proposed structural correspondences: {bridge_blurb}. "
                "Treat as hypotheses pending formal verification and primary sources."
            )
        if level == LevelShift.AVANT_GARDE:
            return (
                f"In a parallel continuum, '{objective}' refracts through {bridge_blurb}— "
                "a speculative cartography of what might yet be built."
            )
        return (
            f"Synthesis map for '{objective}'. "
            f"Key bridges: {bridge_blurb}. "
            "Use the map to explore; label speculative links before acting on them."
        )

    def visualize(self, concept_map: ConceptMap) -> dict[str, Any]:
        return {
            "type": "concept_graph",
            "layout": "force_directed",
            "nodes": [
                {"id": n.id, "label": n.label, "kind": n.kind, "weight": n.weight}
                for n in concept_map.nodes
            ],
            "edges": [
                {
                    "source": b.source_node,
                    "target": b.target_node,
                    "label": b.structural_basis,
                    "novelty": b.novelty,
                    "grounded": b.grounded,
                }
                for b in concept_map.bridges
            ],
            "export": ["json", "svg_stub", "html_canvas_stub"],
        }

    def run(
        self,
        objective: str,
        domains: list[str] | None = None,
        level: LevelShift | str = LevelShift.GENERAL,
    ) -> dict[str, Any]:
        if isinstance(level, str):
            try:
                level = LevelShift(level)
            except ValueError:
                level = LevelShift.GENERAL

        nodes = self.parse(objective)
        if domains:
            for d in domains:
                nodes.append(
                    SemanticNode(
                        id=f"d_{uuid4().hex[:6]}",
                        label=d,
                        kind="domain",
                        domain=d,
                    )
                )
        bridges = self.cross_synthesize(nodes, domains)
        cmap = ConceptMap(objective=objective, nodes=nodes, bridges=bridges, level=level)
        cmap.visualization = self.visualize(cmap)
        narrative = self.level_shift_text(objective, level, bridges)

        logger.info("Weaver map %s nodes=%s bridges=%s level=%s", cmap.id, len(nodes), len(bridges), level)
        return {
            "map_id": cmap.id,
            "objective": objective,
            "level": level.value,
            "nodes": [n.__dict__ for n in nodes],
            "bridges": [b.__dict__ for b in bridges],
            "visualization": cmap.visualization,
            "narrative": narrative,
            "skill": "saphira-weaver",
        }


def weaver_session(
    objective: str,
    domains: list[str] | None = None,
    level: str = "general_synthesis",
) -> dict[str, Any]:
    return WeaverEngine().run(objective, domains=domains, level=level)
