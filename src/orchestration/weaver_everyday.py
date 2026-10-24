"""Everyday Weaver modes: Choice Mapper, Crisis Synthesizer, Energy Tracker, Symptom Detective.

Copyright © 2026 Chelsea Megan Woods
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

logger = logging.getLogger("SaphiraWeaverEveryday")


@dataclass
class ChoiceOption:
    id: str
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)


class ChoiceMapper:
    """Dynamic Choice Matrix from raw decision dumps."""

    def run(
        self,
        dilemma: str,
        options: list[dict[str, Any]] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        options = options or []
        constraints = constraints or {}
        parsed: list[ChoiceOption] = []
        if not options:
            # Heuristic split on "or" / vs
            parts = [p.strip() for p in dilemma.replace(" vs ", " or ").split(" or ") if p.strip()]
            for i, p in enumerate(parts[:6] or [dilemma]):
                parsed.append(ChoiceOption(id=f"opt_{i}", label=p[:120]))
        else:
            for i, o in enumerate(options):
                parsed.append(
                    ChoiceOption(
                        id=o.get("id", f"opt_{i}"),
                        label=str(o.get("label", o))[:120],
                        attributes=dict(o.get("attributes") or {}),
                    )
                )

        tradeoffs = []
        if len(parsed) >= 2:
            a, b = parsed[0], parsed[1]
            tradeoffs.append(
                {
                    "from": a.id,
                    "to": b.id,
                    "summary": (
                        f"Comparing '{a.label}' vs '{b.label}': map time, money, stress, "
                        "and timeline effects against your stated constraints."
                    ),
                    "dimensions": ["time", "money", "stress", "timeline"],
                }
            )

        matrix = {
            "type": "choice_matrix",
            "dilemma": dilemma,
            "options": [{"id": o.id, "label": o.label, "attributes": o.attributes} for o in parsed],
            "tradeoffs": tradeoffs,
            "constraints": constraints,
            "guidance": (
                "This matrix clarifies cause and effect; it does not choose for you. "
                "Adjust weights to match what matters most right now."
            ),
        }
        logger.info("ChoiceMapper options=%s", len(parsed))
        return {"mode": "choice_mapper", "matrix": matrix, "skill": "saphira-weaver-everyday"}


class CrisisSynthesizer:
    """Triage multiple shocks into a 30-day survival path."""

    def run(
        self,
        shocks: list[dict[str, Any]] | None = None,
        budget: dict[str, Any] | None = None,
        notes: str = "",
    ) -> dict[str, Any]:
        shocks = shocks or []
        budget = budget or {}
        if not shocks and notes:
            shocks = [{"label": notes[:160], "urgency": "unknown", "cost": None}]

        ranked = sorted(
            shocks,
            key=lambda s: {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 2}.get(
                str(s.get("urgency", "unknown")).lower(), 2
            ),
        )

        path = {
            "type": "30_day_survival_path",
            "triage_order": [
                {
                    "id": s.get("id", f"shock_{i}"),
                    "label": s.get("label", "item"),
                    "urgency": s.get("urgency", "unknown"),
                    "cost": s.get("cost"),
                    "action": s.get("action")
                    or "Assess safety risk first; defer only if structurally safe.",
                }
                for i, s in enumerate(ranked)
            ],
            "budget_context": budget,
            "negotiation_stubs": [
                "Request itemized bill and hardship adjustment on medical charges.",
                "Ask provider for deferred payment plan before new credit.",
            ],
            "diy_vs_pro": "Prefer DIY only when safety and tools allow; structural water risk escalates to pro.",
            "disclaimer": (
                "Informational triage only—not financial, legal, or medical advice. "
                "No autonomous payments or external commitments."
            ),
        }
        logger.info("CrisisSynthesizer shocks=%s", len(ranked))
        return {"mode": "crisis_synthesizer", "path": path, "skill": "saphira-weaver-everyday"}


class EnergyTracker:
    """Energy-adaptive to-do grid."""

    ENERGY_BANDS = (
        (0, 15, "micro"),
        (16, 40, "light"),
        (41, 70, "moderate"),
        (71, 100, "full"),
    )

    def _band(self, pct: int) -> str:
        pct = max(0, min(100, int(pct)))
        for lo, hi, name in self.ENERGY_BANDS:
            if lo <= pct <= hi:
                return name
        return "micro"

    def run(
        self,
        energy_pct: int,
        tasks: list[dict[str, Any]] | None = None,
        context: str = "",
    ) -> dict[str, Any]:
        tasks = tasks or []
        band = self._band(energy_pct)

        # Difficulty heuristic: explicit or inferred from labels
        def difficulty(t: dict[str, Any]) -> str:
            d = str(t.get("difficulty", "")).lower()
            if d in {"micro", "light", "moderate", "full"}:
                return d
            label = str(t.get("label", "")).lower()
            if any(k in label for k in ("tax", "report", "deep", "write", "code")):
                return "full"
            if any(k in label for k in ("call", "email", "plan")):
                return "moderate"
            if any(k in label for k in ("dish", "laundry", "walk", "water", "tidy")):
                return "micro"
            return "light"

        allowed = {
            "micro": {"micro"},
            "light": {"micro", "light"},
            "moderate": {"micro", "light", "moderate"},
            "full": {"micro", "light", "moderate", "full"},
        }[band]

        filtered = []
        for t in tasks:
            diff = difficulty(t)
            if diff in allowed:
                filtered.append({**t, "difficulty": diff, "eligible": True})
            else:
                filtered.append({**t, "difficulty": diff, "eligible": False})

        next_action = next((t for t in filtered if t.get("eligible")), None)
        if not next_action:
            next_action = {
                "label": "One tiny physical reset (e.g. 5 dishes or a 3-minute stretch)",
                "difficulty": "micro",
                "eligible": True,
            }

        grid = {
            "type": "energy_adaptive_grid",
            "energy_pct": energy_pct,
            "band": band,
            "context": context,
            "tasks": filtered,
            "next_action": next_action,
            "message": (
                f"Energy band '{band}' ({energy_pct}%). "
                f"Do not force high-load work. Next: {next_action.get('label')}."
            ),
        }
        logger.info("EnergyTracker band=%s tasks=%s", band, len(tasks))
        return {"mode": "energy_tracker", "grid": grid, "skill": "saphira-weaver-everyday"}


class SymptomDetective:
    """Passive correlation hints from notes + optional wearable fields. Not a diagnosis."""

    def run(
        self,
        notes: list[dict[str, Any]] | None = None,
        wearable: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        notes = notes or []
        wearable = wearable or []

        # Toy correlation: flag sleep < 6 and sweetener mentions
        low_sleep_days = sum(1 for w in wearable if float(w.get("sleep_hours", 8)) < 6)
        sweetener_notes = [
            n for n in notes if "sweetener" in str(n.get("text", "")).lower()
            or "diet" in str(n.get("text", "")).lower()
        ]
        fatigue_notes = [
            n for n in notes
            if any(k in str(n.get("text", "")).lower() for k in ("tired", "fatigue", "fog", "exhaust"))
        ]

        correlations = []
        if low_sleep_days and fatigue_notes:
            correlations.append(
                {
                    "hypothesis": "Fatigue notes often co-occur with nights under 6 hours sleep.",
                    "confidence": "exploratory",
                    "sample_sleep_low_days": low_sleep_days,
                    "fatigue_note_count": len(fatigue_notes),
                }
            )
        if sweetener_notes and fatigue_notes:
            correlations.append(
                {
                    "hypothesis": "Some fatigue notes appear near mentions of artificial sweeteners or diet drinks.",
                    "confidence": "exploratory",
                    "sweetener_note_count": len(sweetener_notes),
                }
            )
        if not correlations:
            correlations.append(
                {
                    "hypothesis": "Not enough overlapping samples yet—keep casual notes for another week.",
                    "confidence": "insufficient_data",
                }
            )

        experiment = {
            "title": "One low-effort week test",
            "steps": [
                "Keep the same casual notes when you feel off.",
                "Pick one variable (e.g. no artificial sweeteners before noon, or wind-down for 7+ hours in bed).",
                "Compare note frequency at week end—do not treat results as medical fact.",
            ],
        }

        report = {
            "type": "symptom_pattern_map",
            "note_count": len(notes),
            "wearable_samples": len(wearable),
            "correlations": correlations,
            "experiment": experiment,
            "disclaimer": (
                "Not medical advice or diagnosis. Pattern hypotheses only. "
                "Discuss concerning symptoms with a qualified clinician."
            ),
        }
        logger.info("SymptomDetective notes=%s wearable=%s", len(notes), len(wearable))
        return {"mode": "symptom_detective", "report": report, "skill": "saphira-weaver-everyday"}


def run_everyday_mode(mode: str, **kwargs: Any) -> dict[str, Any]:
    mode = (mode or "").lower().replace("-", "_")
    if mode in {"choice", "choice_mapper", "decision"}:
        return ChoiceMapper().run(
            dilemma=kwargs.get("dilemma") or kwargs.get("text") or "",
            options=kwargs.get("options"),
            constraints=kwargs.get("constraints"),
        )
    if mode in {"crisis", "crisis_synthesizer", "triage"}:
        return CrisisSynthesizer().run(
            shocks=kwargs.get("shocks"),
            budget=kwargs.get("budget"),
            notes=kwargs.get("notes") or kwargs.get("text") or "",
        )
    if mode in {"energy", "energy_tracker", "burnout"}:
        return EnergyTracker().run(
            energy_pct=int(kwargs.get("energy_pct", 10)),
            tasks=kwargs.get("tasks"),
            context=kwargs.get("context") or "",
        )
    if mode in {"symptom", "symptom_detective", "habit"}:
        return SymptomDetective().run(
            notes=kwargs.get("notes"),
            wearable=kwargs.get("wearable"),
        )
    return {"error": "unknown_mode", "mode": mode, "supported": [
        "choice_mapper", "crisis_synthesizer", "energy_tracker", "symptom_detective"
    ]}
