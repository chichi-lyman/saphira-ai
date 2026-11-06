"""
agents/novareign/agent.py — NovaReign governance + capability routing
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

Consumes:
  - src/core/capability_entries_web.py  (web / synthesis / ambient)
  - any broader capability registry already present in the repo

Produces a Plan object used by the 6-stage orchestrator.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("saphira.novareign")


@dataclass
class Plan:
    goal: str
    capability_ids: list[str] = field(default_factory=list)
    dispatch: list[str] = field(default_factory=list)
    requires_execution: bool = False
    policy_hints: dict[str, str] = field(default_factory=dict)
    notes: str = ""


def _load_web_capabilities() -> list[dict[str, Any]]:
    try:
        from src.core.capability_entries_web import WEB_AND_AMBIENT_CAPABILITIES
        return list(WEB_AND_AMBIENT_CAPABILITIES)
    except Exception as exc:
        logger.warning("Could not load WEB_AND_AMBIENT_CAPABILITIES: %s", exc)
        return []


def _load_catalog_capabilities() -> list[dict[str, Any]]:
    try:
        from src.core.saphira_capability_catalog import load_capabilities
        caps = load_capabilities()
        if isinstance(caps, list):
            return caps
    except Exception:
        pass
    try:
        import json
        from pathlib import Path
        path = Path("src/core/capabilities.json")
        if path.exists():
            data = json.loads(path.read_text())
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "capabilities" in data:
                return data["capabilities"]
    except Exception:
        pass
    return []


_KEYWORD_MAP = [
    (re.compile(r"\b(search|google|look up|find online|web)\b", re.I), "web_search"),
    (re.compile(r"\b(fetch|open page|read (this|the) (url|page|article)|crawl)\b", re.I), "fetch_page"),
    (re.compile(r"\b(refresh|update|re-?fetch|check again)\b", re.I), "refresh_page"),
    (re.compile(r"\b(summarize|synthesis|brief|key points|compare sources)\b", re.I), "synthesize_research"),
    (re.compile(r"\b(cast|tv|screen|display|chromecast)\b", re.I), "cast_to_display"),
    (re.compile(r"\b(map|directions|navigate|send to phone|open on (my )?phone)\b", re.I), "push_to_device"),
    (re.compile(r"\b(trivia|quiz|game)\b", re.I), "start_trivia"),
    (re.compile(r"\b(music|playlist|play something|background (music|audio))\b", re.I), "set_ambient_music"),
]


class NovaReign:
    name = "novareign"
    default_policy = "ALLOW"

    def __init__(self) -> None:
        self._web_caps = _load_web_capabilities()
        self._catalog = _load_catalog_capabilities()
        self._by_id = {c["id"]: c for c in self._web_caps if "id" in c}
        for c in self._catalog:
            cid = c.get("id") or c.get("capability_id")
            if cid and cid not in self._by_id:
                self._by_id[cid] = c

    def plan(self, goal: str) -> dict:
        p = self._route_text(goal)
        return {
            "agent": self.name,
            "goal": p.goal,
            "dispatch": p.dispatch,
            "capability_ids": p.capability_ids,
            "requires_execution": p.requires_execution,
        }

    async def route(
        self,
        intent: Any,
        perception: Optional[dict] = None,
        capability_registry: bool = True,
    ) -> Plan:
        text = ""
        if hasattr(intent, "text"):
            text = str(intent.text)
        elif hasattr(intent, "raw"):
            text = str(intent.raw)
        elif isinstance(intent, dict):
            text = str(intent.get("text") or intent.get("message") or "")
        else:
            text = str(intent)

        plan = self._route_text(text)

        if perception and perception.get("has_image"):
            if "vision_analyze" in self._by_id and "vision_analyze" not in plan.capability_ids:
                plan.capability_ids.append("vision_analyze")
                plan.requires_execution = True

        return plan

    def _route_text(self, text: str) -> Plan:
        matched: list[str] = []
        policy_hints: dict[str, str] = {}
        dispatch: list[str] = []

        for pattern, cap_id in _KEYWORD_MAP:
            if pattern.search(text or ""):
                if cap_id in self._by_id or not self._by_id:
                    matched.append(cap_id)
                    meta = self._by_id.get(cap_id, {})
                    agent = meta.get("agent")
                    if agent and agent not in dispatch:
                        dispatch.append(agent)
                    if meta.get("policy"):
                        policy_hints[cap_id] = meta["policy"]

        if not matched and text and text.strip().endswith("?"):
            matched.append("web_search")
            if "scholar" not in dispatch:
                dispatch.append("scholar")

        research_caps = {"web_search", "fetch_page", "refresh_page", "synthesize_research", "start_trivia"}
        if any(c in research_caps for c in matched) and "scholar" not in dispatch:
            dispatch.append("scholar")

        device_caps = {"cast_to_display", "push_to_device", "set_ambient_music"}
        if any(c in device_caps for c in matched) and "agent_zero" not in dispatch and "zero" not in dispatch:
            dispatch.append("agent_zero")

        requires_execution = bool(matched)

        if any(c in {"web_search", "fetch_page"} for c in matched) and "synthesize_research" not in matched:
            if re.search(r"\b(summarize|summary|brief|key points|compare)\b", text or "", re.I):
                matched.append("synthesize_research")

        return Plan(
            goal=text,
            capability_ids=matched,
            dispatch=dispatch,
            requires_execution=requires_execution,
            policy_hints=policy_hints,
            notes="routed via capability registry + keyword heuristics",
        )


NovaReignAgent = NovaReign
