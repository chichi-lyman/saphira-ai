# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""
Isolated sandbox execution layer for Saphira AI.

Provides local-first Docker / Playwright isolation and optional cloud fallback
so autonomous browser / CLI tasks never run in the main process address space.
"""

from .browser_driver import BrowserDriver, SandboxSession, SandboxResult
from .credential_vault import CredentialVault, CredentialRef
from .sentinel_gate import SentinelDecision, review_action

__all__ = [
    "BrowserDriver",
    "SandboxSession",
    "SandboxResult",
    "CredentialVault",
    "CredentialRef",
    "SentinelDecision",
    "review_action",
]

__version__ = "0.1.0"
