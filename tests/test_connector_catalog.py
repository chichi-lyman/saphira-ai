"""Fail-closed checks for the connector catalog."""
from src.integrations.connector_catalog import CONNECTORS, connector_readiness, connector_status


def test_catalog_contains_expected_integrations() -> None:
    names = {item.name for item in CONNECTORS}
    assert {"openai", "google_gemini", "xai", "github", "supabase", "notion", "stripe", "celery", "zapier", "twilio", "canva", "figma", "mcp_servers"} <= names
    assert len(names) == len(CONNECTORS)


def test_connectors_are_never_enabled_by_environment_presence() -> None:
    status = connector_status(CONNECTORS[0], {"OPENAI_API_KEY": "test-key"})
    assert status["configured"] is True
    assert status["enabled"] is False
    assert status["status"] == "configured_not_enabled"


def test_missing_credentials_are_reported_without_secret_values() -> None:
    status = connector_status(next(x for x in CONNECTORS if x.name == "stripe"), {})
    assert status["configured"] is False
    assert status["missing_environment"] == ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
    assert "test-key" not in repr(status)


def test_readiness_summary_does_not_claim_connectors_are_live() -> None:
    result = connector_readiness({"NOTION_API_KEY": "test-key"})
    assert result["total"] == len(CONNECTORS)
    assert result["enabled"] == 0
    notion = next(x for x in result["connectors"] if x["name"] == "notion")
    assert notion["configured"] is True
    assert notion["enabled"] is False
