"""Canonical capability catalog for Saphira's background workforce.

Copyright © 2026 Chelsea Megan Woods
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path


class AutonomyLevel(IntEnum):
    OBSERVE = 0
    ASSIST = 1
    EXECUTE = 2
    COMMIT = 3


@dataclass(frozen=True)
class Capability:
    key: str
    description: str
    agent: str
    minimum_autonomy: AutonomyLevel = AutonomyLevel.ASSIST
    reversible: bool = True
    external_side_effect: bool = False
    tags: tuple[str, ...] = ()


def _level(name: str) -> AutonomyLevel:
    return AutonomyLevel[name]


def _load_raw() -> list[dict]:
    here = Path(__file__).resolve().parent
    path = here / "capabilities.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


@dataclass
class CapabilityCatalog:
    capabilities: dict[str, Capability] = field(default_factory=dict)

    @classmethod
    def default(cls) -> "CapabilityCatalog":
        items = []
        for r in _load_raw():
            items.append(
                Capability(
                    key=r["key"],
                    description=r["description"],
                    agent=r["agent"],
                    minimum_autonomy=_level(r["minimum_autonomy"]),
                    reversible=r.get("reversible", True),
                    external_side_effect=r.get("external_side_effect", False),
                    tags=tuple(r.get("tags") or ()),
                )
            )
        return cls({item.key: item for item in items})

    def get(self, key: str) -> Capability | None:
        return self.capabilities.get(key)

    def for_agent(self, agent: str) -> list[Capability]:
        return [c for c in self.capabilities.values() if c.agent == agent]

    def by_tag(self, tag: str) -> list[Capability]:
        return [c for c in self.capabilities.values() if tag in c.tags]

    def competitive_parity_keys(self) -> dict[str, list[str]]:
        tags = (
            "openai-parity",
            "anthropic-parity",
            "google-parity",
            "microsoft-parity",
            "meta-parity",
            "perplexity-parity",
            "xai-parity",
            "deepseek-parity",
            "edge",
        )
        return {t: [c.key for c in self.by_tag(t)] for t in tags}

    def requires_commit_approval(self, key: str) -> bool:
        capability = self.get(key)
        return bool(capability and capability.minimum_autonomy >= AutonomyLevel.COMMIT)
