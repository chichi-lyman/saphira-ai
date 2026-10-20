"""Tenant isolation tests for memory guard."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pytest

from src.platform.memory.tenant_guard import (
    TenantMemoryGuard,
    TenantIsolationError,
    MissingTenantError,
)
from src.platform.memory.hybrid import TenantMemoryStore


@pytest.fixture
def guard():
    return TenantMemoryGuard(store=TenantMemoryStore())


def test_add_requires_tenant(guard):
    with pytest.raises(MissingTenantError):
        guard.add(tenant_id="", user_id="u1", content="x")
    with pytest.raises(MissingTenantError):
        guard.add(tenant_id="t1", user_id="", content="x")


def test_cross_tenant_list_empty(guard):
    guard.add(tenant_id="t-a", user_id="u1", content="secret-a")
    rows_b = guard.list(tenant_id="t-b", user_id="u1")
    assert rows_b == []
    rows_a = guard.list(tenant_id="t-a", user_id="u1")
    assert len(rows_a) == 1
    assert rows_a[0].content == "secret-a"


def test_delete_wrong_tenant_keeps_record(guard):
    rec = guard.add(tenant_id="t-a", user_id="u1", content="keep-me")
    deleted = guard.delete(tenant_id="t-b", user_id="u1", record_id=rec.id)
    assert deleted is False
    still = guard.get(tenant_id="t-a", user_id="u1", record_id=rec.id)
    assert still is not None
    assert still.content == "keep-me"


def test_delete_same_tenant_works(guard):
    rec = guard.add(tenant_id="t-a", user_id="u1", content="gone")
    assert guard.delete(tenant_id="t-a", user_id="u1", record_id=rec.id) is True
    assert guard.get(tenant_id="t-a", user_id="u1", record_id=rec.id) is None


def test_assert_no_leak(guard):
    guard.add(tenant_id="t1", user_id="u1", content="a")
    guard.add(tenant_id="t2", user_id="u2", content="b")
    guard.assert_no_leak(
        tenant_id="t1", user_id="u1", other_tenant_id="t2", other_user_id="u2"
    )
