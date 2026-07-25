# Unit Tests for Executive Functions
# Copyright © 2026 Chelsea Megan Woods

import pytest
from src.core.executive_functions import ExecutiveFunctionModule

def test_prioritize_working_memory():
    ef = ExecutiveFunctionModule()
    items = ["a", "b", "c", "d", "e", "f"]
    result = ef.prioritize_working_memory(items, capacity=3)
    assert len(result) == 3
    assert result == ["a", "b", "c"]

def test_switch_strategy():
    ef = ExecutiveFunctionModule()
    assert ef.switch_strategy("current", 0) == "current"
    assert ef.switch_strategy("current", 1) == "current"
    assert ef.switch_strategy("current", 2) == "alternative_path"

def test_inhibit_noise():
    ef = ExecutiveFunctionModule()
    candidates = ["good", "noise", "relevant"]
    scores = [0.9, 0.2, 0.75]
    result = ef.inhibit_noise(candidates, scores, threshold=0.6)
    assert result == ["good", "relevant"]

def test_sequence_plan():
    ef = ExecutiveFunctionModule()
    plan = ef.sequence_plan("Finish report", ["research", "write", "review"])
    assert plan["goal"] == "Finish report"
    assert len(plan["ordered_steps"]) == 3
    assert plan["estimated_effort"] == "low"
