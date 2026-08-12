"""RBAC, agent DIDs, and scoped API keys."""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

ROLES: Dict[str, Set[str]] = {
    "viewer": {"chat:read", "memory:read"},
    "operator": {"chat:read", "chat:write", "memory:read", "memory:write", "agent:invoke"},
    "admin": {"chat:read", "chat:write", "memory:read", "memory:write", "agent:invoke", "policy:write", "billing:read", "audit:export", "tenant:admin"},
}

@dataclass
class Principal:
    subject_id: str
    tenant_id: str
    roles: List[str] = field(default_factory=list)
    agent_did: Optional[str] = None
    def permissions(self) -> Set[str]:
        perms: Set[str] = set()
        for role in self.roles:
            perms |= ROLES.get(role, set())
        return perms
    def can(self, permission: str) -> bool:
        return permission in self.permissions()

@dataclass
class ApiKeyRecord:
    key_id: str
    tenant_id: str
    hash: str
    scopes: Set[str]
    created_at: float = field(default_factory=time.time)

class IdentityService:
    def __init__(self) -> None:
        self._keys: Dict[str, ApiKeyRecord] = {}
    def issue_api_key(self, tenant_id: str, scopes: Optional[Set[str]] = None) -> str:
        raw = secrets.token_urlsafe(32)
        key_id = secrets.token_hex(8)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        self._keys[key_id] = ApiKeyRecord(key_id=key_id, tenant_id=tenant_id, hash=digest, scopes=scopes or {"chat:write", "agent:invoke"})
        return f"{key_id}.{raw}"
    def verify_api_key(self, token: str) -> Optional[ApiKeyRecord]:
        try:
            key_id, raw = token.split(".", 1)
        except ValueError:
            return None
        rec = self._keys.get(key_id)
        if not rec:
            return None
        if hashlib.sha256(raw.encode()).hexdigest() != rec.hash:
            return None
        return rec
    @staticmethod
    def agent_did(tenant_id: str, agent_name: str) -> str:
        return f"did:saphira:{tenant_id}:{agent_name}"

identity_service = IdentityService()
