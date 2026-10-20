# Saphira × Nova Umbrella — Competitive Layer Registry

**Author:** Chelsea Megan Woods  
**Status:** Capability map + implementation status (not a claim of parity)  
**Date:** 2026-10-20  
**Related:** gap analysis, `NOVA_UMBRELLA_STRESS_TEST_MATRIX.md`, `execution_contract.py`, `leados_workflow.py`

---

## Principle

We do **not** copy Microsoft Foundry, Amazon AgentCore, Google Gemini Agent, or OpenAI Agents SDK wholesale.  
We map each **layer** they dominate to concrete Saphira / Nova Umbrella modules, mark honest status, and implement only what composes with the existing pipeline and the seven-stage contract.

| Status | Meaning |
|--------|---------|
| **implemented** | Code + tests exist in repo; may still need production hardening |
| **partial** | Modules exist; not full enterprise/cloud scale |
| **planned** | Documented target; not yet shipped |
| **out_of_scope_now** | Explicitly deferred (e.g. own GPU farm) |

---

## Layer map (gap-analysis rows → Saphira modules)

### 1. Managed multi-agent runtime
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| Foundry hosted agents, AgentCore Runtime, Gemini sub-agents, OpenAI Agents SDK | Fixed executive pipeline + swarm + execution contract | **partial** | `src/core/orchestrator.py`, `swarm_orchestrator.py`, `live_orchestrator.py`, `execution_contract.py`, `agents/` |
| Session isolation / scale-to-zero | Session context + worker isolation (not hypervisor sandboxes) | **planned** | platform swarm + deployment config |

**Upgrade path:** Keep single public persona (Saphira). Expand specialist delegation behind the contract; do not expose internal agent names.

### 2. Enterprise identity / RBAC / tenant isolation
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| Azure AD, Cognito, dedicated agent identity | Platform identity + RBAC + policy L1/L2/L3 | **partial** | `src/platform/identity/`, `src/platform/policy/`, capability `enterprise.secure` |
| Tenant isolation | Tenant IDs on ExecutionContext + memory scopes | **partial** | `ExecutionContext.tenant_id`, hybrid memory |

**Upgrade path:** Enforce tenant_id on every contract run and memory read/write; no cross-tenant retrieval.

### 3. Tool / MCP / connector ecosystem
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| 1400+ MCP tools, Logic Apps, Bedrock Gateway, Workspace | Nova Connect + MCP-ready adapters | **partial** | `src/connectors/`, `src/integrations/`, GitHub partial |
| Computer use / browser | Policy-controlled automation only | **planned** | gated under execution contract |

**Upgrade path:** Standardize MCP-compatible tool registry; every tool call goes through AUTHORIZE + RESERVE.

### 4. Durable background jobs + recovery
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| AgentCore long runtimes, Foundry routines, Gemini hours/days tasks | Celery/Redis + Commerce state machine + contract retries | **partial** | Redis/Celery foundations, `commerce/states.py`, `execution_contract` max_retries |
| Dead-letter / idempotency | Audit + idempotent Stripe events | **partial** | `stripe_webhooks.py`, audit hash chain |

**Upgrade path:** Production worker pool, DLQ, task ledger keyed by execution_id.

### 5. Memory (persistent, multi-tenant)
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| Managed short/long/procedural memory | Hybrid episodic/semantic memory | **partial** | `src/platform/memory/` |
| User-controlled retention | Explicit retention + delete | **partial** | policy + memory APIs |

**Upgrade path:** Tenant-scoped vectors; consolidation job (durable vs temporary) as in matrix feature 29.

### 6. Observability + evaluation
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| Foundry tracing/evals, AgentCore Evaluations, OpenAI Evals | Evidence store + operational telemetry + matrix_snapshot | **partial** | `src/platform/evidence/`, `operational_telemetry.py`, LeadOS `EvidenceStore` |
| Competitive harness Levels 1–5 | Stress-test matrix program | **planned** | `docs/NOVA_UMBRELLA_STRESS_TEST_MATRIX.md` |

**Upgrade path:** Emit contract stage timings to telemetry; block release on matrix regressions.

### 7. Commerce / spend limits / billing
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| Cloud billing + cost controls | Commerce OS + LeadOS under contract | **implemented (Phase-1)** | `src/commerce/*`, `leados_workflow.py`, authority + audit + Stripe verify |
| Per-workflow budgets | RESERVE stage + entitlements | **partial** | `platform/entitlements/`, contract RESERVE |

**Upgrade path:** Hook entitlements metering into RESERVE; LeadOS → live checkout only after smoke tests.

### 8. Voice / multimodal native
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| Voice Live, Realtime Agents, Gemini multimodal | ElevenLabs + voice session + multimodal registry | **partial** | `saphira_voice.py`, `platform/voice/`, `multimodal_registry.py` |
| Low-latency turn-taking | Streaming voice path | **partial** | voice streaming modules |

**Upgrade path:** Keep voice behind contract; no autonomous outbound voice without L1 approval.

### 9. Self-healing / failure injection testing
| Competitor signal | Saphira / Nova target | Status | Module / path |
|-------------------|----------------------|--------|---------------|
| Recovery, failure injection, content safety | SelfHealingOrchestrator + contract ROLLBACK | **partial** | `src/core/self_healing.py`, execution contract |
| Adversarial eval | Matrix Level 3 | **planned** | stress-test suite |

**Upgrade path:** Wire self_healing into worker paths; record recovery in EvidenceStore.

---

## What was *not* added (on purpose)

- Full Azure AD / Cognito product  
- Hypervisor-isolated hosted agent VMs  
- 1,400 managed MCP tools  
- Proprietary DeepMind long-horizon research stack  
- Self-owned GPU inference farm  

Those remain competitor strengths we integrate with via providers, not rebuild.

---

## Nova Umbrella vs Saphira assistant

| Surface | Role in layers |
|---------|----------------|
| **Saphira AI assistant** | User-facing chat, voice, memory, tools; only public persona |
| **Nova Umbrella** | Products (LeadOS, Automation), shared contract, commerce, connectors, telemetry, multi-product reuse |

Every layer above is shared backend. Products consume it; they do not each reimplement identity, jobs, or billing.

---

## Immediate code targets (already on branch or next commits)

1. `config/nova-umbrella.yaml` — layer status flags (this registry in machine form)  
2. `src/core/execution_contract.py` — gates all consequential paths  
3. `src/commerce/leados_workflow.py` — first product workflow under contract  
4. Capability catalog tags (`microsoft-parity`, etc.) — keep aligned with this registry  
5. Evidence → matrix_snapshot — first measurement of success/denial/latency  

---

*Registry tracks truth. Status only moves to implemented when code + tests exist.*
