"""Tests for everyday Weaver modes.

Copyright © 2026 Chelsea Megan Woods
"""

from src.orchestration.weaver_everyday import (
    ChoiceMapper,
    CrisisSynthesizer,
    EnergyTracker,
    SymptomDetective,
    run_everyday_mode,
)


def test_choice_mapper_matrix():
    out = ChoiceMapper().run(
        "accept higher pay with commute or stay remote but bored",
        constraints={"savings_goal": "house"},
    )
    assert out["mode"] == "choice_mapper"
    assert out["matrix"]["type"] == "choice_matrix"
    assert len(out["matrix"]["options"]) >= 1


def test_crisis_synthesizer_triage():
    out = CrisisSynthesizer().run(
        shocks=[
            {"label": "water heater leak", "urgency": "critical", "cost": 800},
            {"label": "worn brake pad", "urgency": "medium", "cost": 300},
            {"label": "medical bill", "urgency": "high", "cost": 1200},
        ],
        budget={"cash": 500},
    )
    assert out["path"]["type"] == "30_day_survival_path"
    assert out["path"]["triage_order"][0]["urgency"] == "critical"


def test_energy_tracker_filters_high_load():
    out = EnergyTracker().run(
        energy_pct=10,
        tasks=[
            {"label": "do taxes"},
            {"label": "put 5 dishes in dishwasher"},
            {"label": "finish deep work report"},
        ],
    )
    assert out["grid"]["band"] == "micro"
    assert out["grid"]["next_action"]["eligible"] is True


def test_symptom_detective_disclaimer():
    out = SymptomDetective().run(
        notes=[{"text": "3 PM headache after diet soda, tired"}],
        wearable=[{"sleep_hours": 5.5}],
    )
    assert "disclaimer" in out["report"]
    assert out["report"]["type"] == "symptom_pattern_map"


def test_run_everyday_mode_router():
    r = run_everyday_mode("energy", energy_pct=25, tasks=[{"label": "walk"}])
    assert r["mode"] == "energy_tracker"
