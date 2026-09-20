# Copyright © 2026 Chelsea Megan Woods
from packages.saphira_core.registry import AGENTS, list_agents, policy_for
from agents.instinct.agent import InstinctAgent
from agents.apex.agent import ApexAgent
from agents.saphira.agent import SaphiraAgent


def test_registry_has_core_pipeline():
    names = list_agents()
    for required in (
        "saphira",
        "aura",
        "agent_two",
        "novareign",
        "novaaethrea",
        "agent_zero",
        "instinct",
        "apex",
    ):
        assert required in names


def test_instinct_apex_allow():
    assert policy_for("instinct") == "ALLOW"
    assert policy_for("apex") == "ALLOW"
    assert InstinctAgent().content_brief("boundaries")["can_publish"] is True
    assert ApexAgent().recommend("growth")["policy"] == "ALLOW"


def test_saphira_surface():
    out = SaphiraAgent().receive("Hey Saphira, schedule a post")
    assert out["agent"] == "saphira"
