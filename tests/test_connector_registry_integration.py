"""Registry integration tests for the connector catalog."""
from src.integrations.plugin_registry import PluginRegistry, register_connector_catalog


def test_catalog_registration_is_disabled_and_idempotent() -> None:
    registry = PluginRegistry()
    register_connector_catalog(registry)
    first = registry.list()
    assert first
    assert all(not manifest.enabled for manifest in first)
    count = len(first)
    register_connector_catalog(registry)
    assert len(registry.list()) == count


def test_catalog_registration_does_not_create_fake_adapters() -> None:
    registry = PluginRegistry()
    register_connector_catalog(registry)
    assert "notion" in {manifest.name for manifest in registry.list()}
    try:
        import asyncio
        asyncio.run(registry.health("notion"))
    except KeyError:
        pass
    else:
        raise AssertionError("Catalog-only entry must not pretend to have a live adapter")
