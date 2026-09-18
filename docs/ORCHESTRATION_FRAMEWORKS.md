# Multi-Agent Orchestration Frameworks (2026) and Woods Fit

Saphira defines a **fixed sequential pipeline** plus **NovaReign fan-out**. External frameworks are optional adapters — they must not replace security or governance stages.

## Framework landscape (2026)

| Framework | Model | Production maturity | Best for | Woods notes |
|-----------|--------|---------------------|----------|-------------|
| **LangGraph** | Explicit graph / state machine | High | Durable workflows, human-in-the-loop, retries | Strong match for NovaReign DAG + checkpointed pipeline |
| **CrewAI** | Role-based crews | Medium | Fast role prototypes | Maps to extended family roles; weaker on audit durability |
| **AutoGen / AG2** | Conversational multi-agent | Medium (research-strong) | Debate, code collab experiments | Useful for Scholar/Cipher research loops |
| **Microsoft Agent Framework** | AutoGen + Semantic Kernel merge | High (enterprise) | Azure, plugins, MCP | Fit if Microsoft-heavy stack |
| **OpenAI Agents SDK / Swarm-style** | Handoff primitives | Lower–medium | Simple handoffs | Can model Saphira→Aura handoffs |
| **Custom orchestrator** | Project-owned | Highest control | Regulated, audit-heavy systems | **Default for Saphira** |

Industry comparisons in 2026 generally place LangGraph first for production multi-agent share, CrewAI for speed-to-demo, AutoGen evolving toward Microsoft Agent Framework, and a large share of serious systems still on custom orchestration.

## Recommended pattern for chichi-lyman / Saphira

1. Keep the custom pipeline as source of truth (Saphira → … → Agent Zero).
2. Optionally implement NovaReign’s planner as a **LangGraph-style** state graph (nodes = agents, edges = protocol transitions, checkpointer = audit).
3. Model extended family as **Crew-style roles** only inside NovaReign fan-out, still under Agent Two attestation and policy gates.
4. Expose tools via **MCP** (NovaAethrea) regardless of framework.
5. Human-in-the-loop = REQUIRE_APPROVAL nodes.

## Anti-patterns

- Framework agents calling Stripe/email without CommercialAuthorityPolicy
- Skipping Agent Two because a framework “has tools”
- Exposing specialist names in user-visible transcripts

## Related

- [AGENT_INTERACTION_PROTOCOLS.md](./AGENT_INTERACTION_PROTOCOLS.md)
- [AGENT_ALIGNMENT.md](./AGENT_ALIGNMENT.md)
