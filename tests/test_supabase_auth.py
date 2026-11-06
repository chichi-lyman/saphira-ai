from __future__ import annotations
import pytest
from fastapi import HTTPException
from src.governance.authentication.supabase_auth import get_current_user

@pytest.mark.asyncio
async def test_missing_bearer_token_is_rejected() -> None:
    with pytest.raises(HTTPException) as error:
        await get_current_user(None)
    assert error.value.status_code == 401

@pytest.mark.asyncio
async def test_missing_supabase_configuration_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    with pytest.raises(HTTPException) as error:
        await get_current_user("Bearer test-token")
    assert error.value.status_code == 503

@pytest.mark.asyncio
async def test_valid_supabase_identity_is_returned(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    class Response:
        status_code = 200
        @staticmethod
        def json() -> dict:
            return {"id": "f3a8b8c0-8d10-4f3d-8f4c-5fba0f88f111",
                    "email": "member@example.com", "app_metadata": {"provider": "email"}}
    class Client:
        async def __aenter__(self): return self
        async def __aexit__(self, *_args): return None
        async def get(self, url: str, headers: dict):
            assert url == "https://example.supabase.co/auth/v1/user"
            assert headers["Authorization"] == "Bearer test-token"
            assert headers["apikey"] == "sb_publishable_test"
            return Response()
    monkeypatch.setattr("src.governance.authentication.supabase_auth.httpx.AsyncClient",
                        lambda timeout: Client())
    user = await get_current_user("Bearer test-token")
    assert user.id == "f3a8b8c0-8d10-4f3d-8f4c-5fba0f88f111"
    assert user.email == "member@example.com"
    assert user.app_metadata["provider"] == "email"
