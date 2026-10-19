# Open-Source Agent Harnesses, Skills & Tools

Curated collection of powerful open-source skills, tools, and agent harnesses across GitHub, organized by domain. Use for competitive awareness, capability benchmarking, and selective integration patterns into the Saphira / Nova Umbrella stack.

**Owner context:** Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Saphira AI

---

## Multi-Agent Swarms & Autonomous Frameworks

| Project | Description |
|---------|-------------|
| **[ruvin/ruflo](https://github.com/ruvin/ruflo)** | Next-generation multi-agent swarm harness that coordinates autonomous agent workflows, adaptive memory, and vector RAG across native agents like Claude Code, Codex, and Hermes. |
| **[stablyai/orca](https://github.com/stablyai/orca)** | Fleet manager and orchestration platform for running multi-agent teams across desktop, mobile, and remote runtime environments. |
| **[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)** | Advanced agent framework optimized for autonomous tool usage, function execution, and multi-step reasoning models. |

**Saphira relevance:** Compare swarm topology and memory hand-off patterns with the six-core chain (Saphira → Aura → Agent Two → Nova Reign → NovaAethrea → Agent Zero). Ruflo and Orca are useful references for fleet-level orchestration; Hermes for tool-calling depth.

---

## Terminal, CLI & Code Base Intelligence

| Project | Description |
|---------|-------------|
| **[anthropics/claude-code](https://github.com/anthropics/claude-code)** | Terminal-native agentic coding tool that executes terminal workflows, manages Git commits, and refactors large codebases directly from command-line prompts. |
| **[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)** | Universal wrapper framework designed to convert standard GUI applications and APIs into agent-native CLI tools. |
| **[yamadashy/repomix](https://github.com/yamadashy/repomix)** | CLI tool that packages entire codebases into structured, compressed single-file context payloads optimized for LLMs and agent ingestion. |

**Saphira relevance:** Strong patterns for agent-native terminal surfaces and codebase packaging. Repomix-style context compression aligns with local-first and offline RAG goals; CLI-Anything is a model for turning accessibility / device actions into tool calls.

---

## Context Compression & Long-Term Agent Memory

| Project | Description |
|---------|-------------|
| **[headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)** | High-performance context compressor and MCP server that strips 60–95% of unnecessary tokens from logs, RAG chunks, and JSON before reaching the model context window. |
| **[akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory)** | Universal long-term memory layer for agent CLIs, facilitating seamless state transfer and context handoffs across different agent frameworks. |
| **[MemPalace/mempalace](https://github.com/MemPalace/mempalace)** | Persistent agent memory engine powered by ChromaDB, structured for ultra-fast vector retrieval and contextual historical recall. |

**Saphira relevance:** Directly informs improvements to `src/memory/ledger.py`, dual-tier RAM + durable store, offline cache sync, and any future MCP memory server. Headroom is especially relevant for token budget discipline on mobile / edge.

---

## Security, Audit & Supply Chain Defense

| Project | Description |
|---------|-------------|
| **[perplexityai/bumblebee](https://github.com/perplexityai/bumblebee)** | Zero-dependency, read-only Go security scanner that audits dependencies, Model Context Protocol (MCP) servers, VS Code extensions, and browser extensions for supply chain vulnerabilities. |
| **[trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge)** | Comprehensive repository of system administration tools, one-liners, security research utilities, and network analysis commands. |

**Saphira relevance:** Bumblebee-style read-only scanning is a good model for hardening the plugin / MCP / connector surface. Aligns with existing AST code guardrails and the broader Aegis / security auditor skill direction.

---

## Integration Notes for Saphira

1. **Do not vendor blindly** — evaluate license, maintenance activity, and attack surface before any dependency or MCP adoption.
2. **Prefer patterns over code** — extract orchestration, memory hand-off, and compression ideas into first-party modules under `src/` and `skills/`.
3. **Security first** — any new tool-forging or code-execution path must still pass AST guardrails and (when available) the isolated sandbox boundary.
4. **Offline / edge** — favor projects that support local vector stores, token compression, and CLI/agent operation without constant cloud round-trips.

---

*Last curated: 2026-10-19. Expand this list as new high-signal harnesses appear; keep entries short and actionable.*
