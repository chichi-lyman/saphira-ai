from __future__ import annotations

import pytest
from fastapi import HTTPException

from src.api.memory_router import _authorize


def test_memory_auth_fails_closed_when_key_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SAPHIRA_MEMORY_API_KEY", raising=False)
    with pytest.raises(HTTPException) as exc:
        _authorize("anything")
    assert exc.value.status_code == 503


def test_memory_auth_rejects_wrong_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SAPHIRA_MEMORY_API_KEY", "test-secret")
    with pytest.raises(HTTPException) as exc:
        _authorize("wrong")
    assert exc.value.status_code == 401


def test_memory_auth_accepts_matching_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SAPHIRA_MEMORY_API_KEY", "test-secret")
    _authorize("test-secret")
