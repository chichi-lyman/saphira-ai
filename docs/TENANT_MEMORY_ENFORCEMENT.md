# Tenant Enforcement on Memory — Explanation

**Author:** Chelsea Megan Woods  
**Status:** Implemented (guard layer on existing hybrid memory)  
**Date:** 2026-10-20

---

## What “tenant enforcement” means

Saphira may serve multiple customers (tenants) and many users. Memory must never leak:

- Tenant A must never see Tenant B’s facts, conversations, or semantic distillations  
- User X under Tenant A must not see User Y’s private memories under the same tenant (unless a future shared-space feature is explicitly designed)

**Tenant enforcement** is the set of rules and code that make those leaks impossible at the memory API boundary.

---

## How it works in Saphira

### 1. Data model (already in `hybrid.py`)

Every `MemoryRecord` stores:

- `tenant_id`  
- `user_id`  
- `kind` (episodic | semantic | …)  
- `content`, `confidence`, `metadata`

There is no global “all memories” list exposed to agents.

### 2. Hard guard (`TenantMemoryGuard`)

All platform/agent code should call the guard, not the raw store:

| Operation | Rule |
|-----------|------|
| **add** | Requires non-empty `tenant_id` + `user_id`. Refuses anonymous writes. |
| **list** | Filters by exact tenant_id **and** user_id. Re-checks every row (defense in depth). |
| **get** | Returns a record only if it belongs to the same tenant+user. |
| **delete** | Deletes only matching tenant+user rows. If the id belongs to another tenant, raises `TenantIsolationError` and leaves the row intact. |
| **distill_semantic** | Promotes episodic → semantic **only within** the same tenant+user. |

Missing ids → `MissingTenantError`  
Cross-tenant access → `TenantIsolationError` (subclass of `PermissionError`)

### 3. Link to the seven-stage contract

`ExecutionContext` carries `tenant_id` and `user_id`.  
Any memory write during EXECUTE should pass:

```text
tenant_memory.add(
    tenant_id=ctx.tenant_id,
    user_id=ctx.user_id,
    content=...,
    execution_id=ctx.execution_id,
)
```

If `ctx.tenant_id` is missing, the guard fails the stage instead of writing to a shared bucket.

### 4. Isolation key

`isolation_key(tenant_id, user_id)` → short hash for indexes and metadata. Used for sharding and audit, not as a secret.

---

## What this does *not* claim

- It is not full enterprise multi-tenant SaaS isolation (network, DB row-level security, KMS per tenant).  
- Production deployments should still put Postgres/pgvector RLS or equivalent under the store.  
- The guard is the **application-level** contract so agents and workflows cannot bypass isolation even if a lower layer is misconfigured.

---

## Microsoft / Amazon / Google / OpenAI integrations

These are **provider endpoints** in `ProviderRegistry`, not separate Saphira brains:

| Provider | Registry key | Env flags / secrets |
|----------|--------------|---------------------|
| OpenAI | `openai_primary` | `OPENAI_API_KEY`, `OPENAI_ENABLED` |
| Microsoft (Azure OpenAI) | `azure_openai` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_ENABLED` |
| Amazon (Bedrock) | `bedrock_primary` | AWS credentials / role, `BEDROCK_ENABLED` |
| Google (Gemini) | `gemini_primary` | `GEMINI_API_KEY`, `GEMINI_ENABLED` |
| xAI | `xai_primary` | `XAI_API_KEY`, `XAI_ENABLED` |
| Local | `vllm_local`, `ollama_local` | local only |

Routing picks the first enabled endpoint that has credentials and the required capability. Secrets never enter git.

---

## Tests to keep green

- Add under tenant A, list under tenant B → empty  
- Delete with wrong tenant → `TenantIsolationError`, record still present  
- Missing tenant_id on add → `MissingTenantError`  
- `assert_no_leak` helper for CI  

---

*Isolation is a product requirement, not an optional feature flag.*
