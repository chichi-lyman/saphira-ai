"""Route user intents toward Saphira excellence pillars.

Does not replace the main orchestrator — suggests which excellence path
should be prioritized for a given request class.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .agent_map import owners_for_pillar
from .pillars import EXCELLENCE_PILLARS, get_pillar


@dataclass(frozen=True)
class ExcellenceRoute:
    pillar_id: str
    capability: str
    plugin: str
    internal_owners: tuple[str, ...]
    reason: str


_KEYWORD_PILLARS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("voice", "speak", "listen", "wake", "tts", "stt", "latency", "fast"), "latency"),
    (("remember", "recall", "memory", "forgot", "history"), "memory"),
    (("automate", "tool", "run", "execute", "workflow", "a11y"), "automation"),
    (("offline", "edge", "local", "on-device", "airplane"), "edge"),
    (("reason", "think", "analyze", "prove", "why", "compare"), "reasoning"),
    (("privacy", "private", "ledger", "self-host", "own my data", "delete my data"), "privacy"),
)


def route_excellence(text: str, *, prefer: Iterable[str] | None = None) -> list[ExcellenceRoute]:
    """Return ordered excellence routes for a user utterance."""
    lowered = (text or "").lower()
    selected: list[str] = []

    if prefer:
        for p in prefer:
            if p not in selected:
                selected.append(p)

    for keywords, pillar_id in _KEYWORD_PILLARS:
        if any(k in lowered for k in keywords) and pillar_id not in selected:
            selected.append(pillar_id)

    # Default companion path always includes latency + privacy posture.
    for fallback in ("latency", "privacy"):
        if fallback not in selected:
            selected.append(fallback)

    routes: list[ExcellenceRoute] = []
    for pillar_id in selected:
        try:
            pillar = get_pillar(pillar_id)
        except KeyError:
            continue
        owners = tuple(owners_for_pillar(pillar_id))
        routes.append(
            ExcellenceRoute(
                pillar_id=pillar.id,
                capability=pillar.capability,
                plugin=pillar.plugin,
                internal_owners=owners,
                reason=pillar.notes,
            )
        )
    return routes


class ExcellenceRouter:
    """Thin wrapper used by orchestrator / control plane."""

    def route(self, text: str, **kwargs) -> list[ExcellenceRoute]:
        return route_excellence(text, **kwargs)

    def catalog(self) -> list[dict]:
        return [
            {
                "id": p.id,
                "title": p.title,
                "target": p.saphira_target,
                "capability": p.capability,
                "plugin": p.plugin,
                "owners": owners_for_pillar(p.id),
            }
            for p in EXCELLENCE_PILLARS
        ]
