# Saphira AI — Sentinel Gate + Isolated Sandbox

**Status:** Implemented (packages/saphira_core/sandbox + agents/cipher)  
**Owner:** Chelsea Megan Woods  
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**

## Purpose

Bring Meta-style VM isolation and explicit Sentinel guardrails into the
Nova Umbrella control plane while preserving Saphira’s local-first,
privacy-respecting identity.

## Architecture

```
User → Saphira (surface)
         → Executive Routing
              ├─ Standard sub-agents (Aura, Lyra, Apex, …)
              └─ Autonomous Task path
                     → Agent Cipher (Sentinel)
                           • prompt-injection filter
                           • credential vault inbound
                           • action approval gate
                     → Isolated Sandbox
                           • local Playwright / Docker
                           • optional cloud fallback
```

## Components

| Layer | Location | Role |
|-------|----------|------|
| Sentinel Gate | `packages/saphira_core/sandbox/sentinel_gate.py` | Heuristic injection scan + critical-action approval |
| Credential Vault | `packages/saphira_core/sandbox/credential_vault.py` | Zero-trust opaque refs; secrets never enter LLM context |
| Browser Driver | `packages/saphira_core/sandbox/browser_driver.py` | Isolated session management (local / Docker / cloud) |
| Agent Cipher | `agents/cipher/agent.py` | Pipeline-facing gatekeeper + vault helpers |
| DOM Action Schema | `agents/cipher/schemas/dom_action.json` | Contract for actions that require review |

## Safety Rules

1. Fail closed when the Sentinel package cannot be imported.
2. Critical actions (payment, account modify, credential export, …) always
   return `REQUIRE_APPROVAL` until the user confirms.
3. Credential values are resolved only inside the sandbox process.
4. External page / email content is scanned for classic prompt-injection
   patterns before any further processing.
5. Only `http://` / `https://` schemes are permitted for navigation.

## Immediate usage

```python
from agents.cipher.agent import CipherAgent

cipher = CipherAgent()

# 1. Register a secret (returns opaque ref only)
ref = cipher.register_credential("email", "primary Gmail", "user@example.com")

# 2. Gate an action
decision = cipher.gate({
    "type": "fill_credential",
    "url": "https://accounts.example.com/login",
    "credential_refs": [ref["ref_id"]],
})

# 3. Open an isolated session only after ALLOW / user confirmation
if decision["verdict"] == "ALLOW":
    session = cipher.open_sandbox()
```

## Production notes

- Set `SAPHIRA_ENCRYPTION_KEY` for at-rest encryption of vault entries.
- Set `SAPHIRA_SANDBOX_DOCKER=1` to prefer Docker isolation.
- Wire real Playwright / Browserbase calls inside `BrowserDriver` methods
  when moving from contract to full runtime execution.
