# Agent Zero — Architecture Notes

**Role in Pipeline:** Final execution engine  
**Pipeline Position:** Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → **Agent Zero**

---

## Current Implementation Summary (as of 2026-10-19)

### Location
- Primary: `src/agents/agent_zero.py`
- Package stub: `agents/agent_zero/`

### Core Responsibilities
Agent Zero is the **hands-on execution engine**. It receives fully authorized, policy-checked payloads from upstream agents and performs the actual side-effecting work.

Current supported action classes:
- Smart-home / Matter / Home Assistant (`turn_on`, `turn_off`, `toggle`, `set_brightness`, `set_temperature`, `lock`, `unlock`, `set_cover`, `matter`)
- Generic system / script execution (placeholder acceptance path)

### Class Structure
```python
class AgentZero:
    def __init__(self, router=None):
        self.router = router
        self.matter = matter_ha          # Matter / Home Assistant connector

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "")
        params = payload.get("params", {})
        # Smart-home path or generic execution acceptance
```

### Key Characteristics
- **Default policy posture:** Execution only after upstream security (Agent Two) and governance (Nova Reign) have cleared the request.
- **No autonomous planning:** Agent Zero does not decide *what* to do; it executes *what has already been approved*.
- **Observability:** Uses structured logging under logger name `"AgentZero"`.
- **Extensibility surface:** New execution backends (shell, Docker, cloud functions, additional smart-home protocols, browser automation under Agent Two supervision, etc.) should be added here or via thin adapters registered through the capability registry / mcp-builder.

### Relationship to Other Agents
| Upstream | Interaction |
|----------|-------------|
| NovaAethrea | Supplies expanded context, memory, and tool schemas |
| Nova Reign | Final policy / approval gate before execution |
| Agent Two | Security review of any high-risk actions (browser, network, secrets) |
| Aura | Perception context that may influence which devices/entities are targeted |

### Current Maturity
- Functional for Matter/Home Assistant smart-home control.
- Generic execution path is still a lightweight acceptance stub — high-leverage area for expansion (sandboxed command execution, container jobs, verified tool calls).
- Strong candidate for increased test coverage and structured result schemas as monetization and multi-tenant features land.

### Recommended Near-Term Hardening (aligned with exit-value roadmap)
1. Richer, typed result schema (success / partial / failed + structured error codes).
2. Explicit support for capability-registry tool calls (so mcp-builder outputs become first-class executable units).
3. Container-friendly design (no host-path assumptions) to support the Docker packaging goal.
4. Audit log emission for every execution (feeds future MRR / usage metering).

---

**Copyright © 2026 Chelsea Megan Woods**
