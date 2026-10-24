# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""
Zero-trust credential vault.

LLM agents never see raw secrets. They receive only opaque CredentialRef
identifiers. The vault resolves the real value inside the isolated sandbox
process at the moment of DOM / form injection.
"""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger("saphira.sandbox.vault")


class CredentialKind(str, Enum):
    EMAIL = "email"
    PASSWORD = "password"
    API_TOKEN = "api_token"
    PAYMENT = "payment"
    OAUTH = "oauth"
    OTHER = "other"


@dataclass(frozen=True)
class CredentialRef:
    """Opaque handle returned to the LLM / agent layer."""
    ref_id: str
    kind: CredentialKind
    label: str  # human-readable, non-secret (e.g. "primary Gmail")
    domain_hint: Optional[str] = None  # e.g. "accounts.google.com"


@dataclass
class _StoredCredential:
    ref: CredentialRef
    # In production this value is encrypted at rest (SAPHIRA_ENCRYPTION_KEY).
    # For the initial implementation we keep it in-process only.
    value: str
    owner_tenant: str = "default"


class CredentialVault:
    """
    In-process + encrypted-at-rest vault.

    Production deployments must load secrets from a real secret manager
    (Railway secrets, AWS Secrets Manager, HashiCorp Vault, etc.) and
    never persist plaintext in the monorepo.
    """

    def __init__(self) -> None:
        self._store: Dict[str, _StoredCredential] = {}
        self._encryption_key = os.getenv("SAPHIRA_ENCRYPTION_KEY", "")
        if not self._encryption_key:
            logger.warning(
                "SAPHIRA_ENCRYPTION_KEY not set — vault running in ephemeral mode only"
            )

    def register(
        self,
        kind: CredentialKind,
        label: str,
        value: str,
        *,
        domain_hint: Optional[str] = None,
        tenant: str = "default",
    ) -> CredentialRef:
        """Register a secret and return an opaque ref the LLM can safely hold."""
        if not value:
            raise ValueError("Credential value cannot be empty")
        ref_id = f"cred_{kind.value}_{secrets.token_hex(6)}"
        ref = CredentialRef(
            ref_id=ref_id,
            kind=kind,
            label=label,
            domain_hint=domain_hint,
        )
        self._store[ref_id] = _StoredCredential(
            ref=ref,
            value=value,
            owner_tenant=tenant,
        )
        logger.info(
            "vault.registered ref=%s kind=%s label=%s",
            ref_id,
            kind.value,
            label,
        )
        return ref

    def resolve(self, ref_id: str, *, tenant: str = "default") -> Optional[str]:
        """
        Resolve a credential for injection inside the sandbox only.

        Never call this from the main LLM context path.
        """
        entry = self._store.get(ref_id)
        if entry is None:
            logger.warning("vault.resolve_miss ref=%s", ref_id)
            return None
        if entry.owner_tenant != tenant and tenant != "system":
            logger.warning("vault.tenant_mismatch ref=%s", ref_id)
            return None
        return entry.value

    def describe(self, ref_id: str) -> Optional[CredentialRef]:
        """Return the non-secret metadata for an existing ref."""
        entry = self._store.get(ref_id)
        return entry.ref if entry else None

    def revoke(self, ref_id: str) -> bool:
        if ref_id in self._store:
            del self._store[ref_id]
            logger.info("vault.revoked ref=%s", ref_id)
            return True
        return False

    def list_refs(self, *, tenant: str = "default") -> list[CredentialRef]:
        return [
            e.ref
            for e in self._store.values()
            if e.owner_tenant == tenant
        ]


# Process-wide vault instance (backed by env / secret manager in production)
credential_vault = CredentialVault()
