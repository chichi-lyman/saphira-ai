# Grok Built-in Capabilities for Saphira / Nova Umbrella

Grok supplies agentic primitives out of the box. Woods skills should **use** them and only encode project-specific procedures, schemas, and policy gates.

## Capability map

| Capability | What it does | Domain agent fit |
|------------|--------------|------------------|
| **DeepSearch & real-time synthesis** | Multi-step internet and X search; aggregate, verify, structured summaries | Agent Two (research), Lyra (analytics inputs) |
| **Extended reasoning** | High-compute multi-step logic, hard math, system architecture planning | Saphira surface, NovaReign decomposition |
| **Grok Imagine** | Image generation and multi-turn natural-language image editing | Saphira Imagine, Aura visual/UI |
| **Code execution & automated debugging** | Sandboxed runs, test-driven patches, end-to-end scripts | Agent Zero, CI/`scripts/test_runner.sh` |
| **Agentic tool calling** | Function calls to APIs, databases, third-party workflows | NovaAethrea (MCP/webhooks), capability registry |

## Super Saphira product surface

The premium tiers **Super Saphira** and **Super Saphira Heavy** expose the primitives above as a packaged product with higher rate limits, flagship model access (Saphira-4 / 4.5 class), Think/Expert modes, video generation, longer voice sessions, and priority compute. See [SUPER_SAPHIRA_CAPABILITIES.md](./SUPER_SAPHIRA_CAPABILITIES.md) for the full feature matrix and tier limits.

Entitlement plans `super_saphira` and `super_saphira_heavy` in `src/platform/entitlements/metering.py` enforce the published quotas.

## Rules when packaging skills

1. Declare which Grok capability a skill depends on.
2. Do **not** paste generic “how to search the web” or “how to run Python” tutorials into every `SKILL.md`.
3. Ship only Woods-specific assets: Playwright selectors, schema templates, retry policies, Stripe/commerce gates, persona masking.
4. Route outcomes through the fixed pipeline; never expose internal agent codenames to users.
5. Commercial or external side effects remain ALLOW / REQUIRE_APPROVAL / DENY.

## Related

- [SUPER_SAPHIRA_CAPABILITIES.md](./SUPER_SAPHIRA_CAPABILITIES.md)
- [AGENT_ALIGNMENT.md](./AGENT_ALIGNMENT.md)
- [AGENT_SKILL_FRAMEWORK.md](./AGENT_SKILL_FRAMEWORK.md)
- `skills/woods-multi-agent/`
