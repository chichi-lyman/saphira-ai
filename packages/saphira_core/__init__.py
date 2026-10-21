"""Shared Saphira core package (monorepo)."""

__version__ = "0.3.0"

# Sandbox + Sentinel surface (VM-isolation / zero-trust credential proxy)
from .sandbox import (  # noqa: F401
    BrowserDriver,
    SandboxSession,
    SandboxResult,
    CredentialVault,
    CredentialRef,
    SentinelDecision,
    review_action,
)

__all__ = [
    "BrowserDriver",
    "SandboxSession",
    "SandboxResult",
    "CredentialVault",
    "CredentialRef",
    "SentinelDecision",
    "review_action",
]
