"""Tests for The Weaver synthesis engine.

Copyright © 2026 Chelsea Megan Woods
"""

from src.orchestration.weaver import WeaverEngine, LevelShift, weaver_session


def test_parse_produces_nodes():
    eng = WeaverEngine()
    nodes = eng.parse("botany meets gothic architecture and vaults")
    assert len(nodes) >= 2


def test_cross_synthesize_bridge():
    eng = WeaverEngine()
    nodes = eng.parse("plant cell walls and gothic vaults")
    bridges = eng.cross_synthesize(nodes, domains=["botany", "architecture"])
    assert len(bridges) >= 1
    assert bridges[0].grounded is False


def test_level_shift_modes():
    eng = WeaverEngine()
    nodes = eng.parse("cooking and astrophysics")
    bridges = eng.cross_synthesize(nodes)
    for level in LevelShift:
        text = eng.level_shift_text("cooking + astrophysics", level, bridges)
        assert len(text) > 20


def test_full_session():
    result = weaver_session(
        "skateboarding and structural law",
        domains=["sports", "law"],
        level="general_synthesis",
    )
    assert "map_id" in result
    assert "visualization" in result
    assert result["visualization"]["type"] == "concept_graph"
    assert result["skill"] == "saphira-weaver"
