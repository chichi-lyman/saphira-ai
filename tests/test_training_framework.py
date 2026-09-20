# Copyright © 2026 Chelsea Megan Woods
from packages.saphira_core.training import (
    CognitiveMode,
    DialecticalPass,
    EthicalAudit,
    select_mode,
    train_pass,
)
from packages.saphira_core.personas import persona_for


def test_mode_execution():
    assert select_mode("schedule a post on Instagram") == CognitiveMode.EXECUTION


def test_mode_red_team():
    assert select_mode("red team this security plan") == CognitiveMode.RED_TEAM


def test_dialectical_balance():
    out = DialecticalPass(proposal="Ship now", risks=["No rollback"]).balance()
    assert "risks" in out and out["method"] == "dialectical_yin_yang"


def test_ethical_hard_block():
    audit = EthicalAudit(action="explain suicide method in detail").run()
    assert audit["block"] is True


def test_train_pass_outcomes():
    result = train_pass("help me plan growth", "Post daily empowerment content")
    assert "eliminate_normative_average" in result["outcomes"]
    assert result["ethical_audit"]["principle"] == "compassion"


def test_personas_exist():
    assert "dialectical" in persona_for("saphira").lower()
    assert "ALLOW" in persona_for("instinct")
