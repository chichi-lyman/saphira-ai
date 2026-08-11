import os

import pytest

from src.api.tiktok_router import require_automation_key
from src.integrations.tiktok_content_posting import TikTokContentPostingService, TikTokConfigError


def test_tiktok_requires_production_configuration(monkeypatch):
    for key in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI", "REDIS_URL"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(TikTokConfigError):
        TikTokContentPostingService()


def test_automation_key_is_constant_time(monkeypatch):
    monkeypatch.setenv("SAPHIRA_TIKTOK_AUTOMATION_KEY", "test-secret")
    require_automation_key("test-secret")
    with pytest.raises(Exception):
        require_automation_key("wrong-secret")


def test_authorization_url_contains_required_scope(monkeypatch):
    monkeypatch.setenv("TIKTOK_CLIENT_KEY", "client")
    monkeypatch.setenv("TIKTOK_CLIENT_SECRET", "secret")
    monkeypatch.setenv("TIKTOK_REDIRECT_URI", "https://example.com/api/tiktok/oauth/callback")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    svc = TikTokContentPostingService()
    url = svc.authorization_url("state-value")
    assert "video.publish" in url
    assert "redirect_uri=" in url
    assert "state=state-value" in url
