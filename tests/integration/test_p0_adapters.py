from src.integrations.p0_adapters import (
    ASICoreAdapter,
    SalesSwarmAdapter,
    SentinelAdapter,
    SaphiraOSAdapter,
    TwinVaultAdapter,
)


def test_asi_core_formulates_directive():
    result = ASICoreAdapter().formulate_directive("audit the sales workflow")
    assert result["status"] == "DIRECTIVE_FORMULATED"
    assert len(result["strategic_plan"]) == 3


def test_sales_swarm_requires_approval():
    result = SalesSwarmAdapter().plan("HVAC", "Atlanta, GA", 5)
    # Must match SalesSwarmAdapter.plan() contract (approval-gated pipeline)
    assert result["workflow"] == ["scout", "profile", "qualify", "draft", "approval"]
    assert result["approval_required"] is True
    assert result["status"] == "PENDING_APPROVAL"


def test_sentinel_green_path():
    result = SentinelAdapter().scan("node-1", {"failed_auth_attempts": 1})
    assert result["threat_status"] == "GREEN"
    assert result["anomalous"] is False


def test_sentinel_red_path():
    result = SentinelAdapter().scan("node-1", {"failed_auth_attempts": 4})
    assert result["threat_status"] == "RED"
    assert result["anomalous"] is True


def test_twin_vault_only_stores_reference():
    vault = TwinVaultAdapter()
    vault.put_reference("github", "secret://github-token")
    assert vault.get_reference("github") == "secret://github-token"
