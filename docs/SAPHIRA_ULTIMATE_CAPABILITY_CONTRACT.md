# Saphira AI — Ultimate Capability Contract

This document is the canonical capability contract for Saphira's autonomous executive-assistant architecture. Saphira remains the single conversational identity; specialized agents operate as background workers.

## 1. Conversational intelligence
- Multimodal chat: text, image, audio, screen/context inputs.
- Adaptive persona and tone engine.
- Low-latency voice pipeline with interruption/barge-in support.
- Speech-to-text and streaming text-to-speech adapters.
- Wake/presence support where the host platform permits it.
- Conversation context plus operational memory.

## 2. Autonomous execution
- Goal decomposition into inspectable task graphs.
- Capability-based agent routing.
- Background worker execution.
- Dependencies, retries, timeouts, cancellation, and failure isolation.
- Verification/QA before final completion.
- Durable task history and artifacts.
- Proactive schedules and event-triggered tasks.

## 3. Core agents
1. Orchestrator / Supervisor — plans, delegates, coordinates, resolves conflicts.
2. Samantha Persona — conversational presentation, tone, empathy, response formatting.
3. STEM/Math — deterministic calculations and tool-grounded technical reasoning.
4. CAD/3D — OpenSCAD/build123d-style model generation and validation adapters.
5. Developer — code generation, tests, debugging, refactoring, sandbox execution.
6. Vision/Screen — OCR, screenshots, image/video interpretation, spatial context.
7. Voice/Audio — STT/TTS streaming, interruption handling, audio state.
8. OS/Hardware — device telemetry, files, applications, timers, diagnostics through explicit host adapters.
9. IoT/Smart Environment — Home Assistant/Matter/device integrations through permissioned adapters.
10. Web Grounding — live search, retrieval, fact verification, weather/navigation adapters.
11. Memory — session, semantic, episodic, procedural, preference, and task memory.
12. Proactive Planner — schedules, events, monitoring, notifications, recurring workflows.
13. Communications — email/messaging/outreach preparation and execution behind approval gates.
14. Commerce — Shopify/store/product/order workflows behind permissioned integrations.
15. QA/Verifier — validates agent outputs and checks task completion criteria.

## 4. System integration contract
Real-world control is adapter-based. The core must not assume unrestricted operating-system access. Every adapter exposes declared capabilities, scopes, audit events, and an autonomy requirement.

Examples:
- `filesystem.read`, `filesystem.write`
- `process.inspect`, `process.launch`
- `device.telemetry`
- `browser.search`, `browser.fetch`
- `calendar.read`, `calendar.write`
- `communications.draft`, `communications.send`
- `commerce.catalog`, `commerce.order`
- `iot.read`, `iot.control`
- `code.sandbox.execute`
- `cad.generate`, `cad.validate`
- `research.cite`, `research.factcheck`
- `media.generate`, `agent.workflow`, `model.route`

## 5. Autonomy policy
- L0 Observe: read-only inspection and analysis.
- L1 Assist: drafts and reversible local work.
- L2 Execute: approved/reversible actions may run automatically.
- L3 Commit: external, financial, destructive, public, or irreversible actions require explicit approval.

The policy engine is evaluated before every sensitive tool invocation, not only when a task begins.

## 6. Memory model
Saphira should distinguish:
- Session memory — current conversation.
- Episodic memory — completed tasks and important events.
- Semantic memory — durable facts and project knowledge.
- Procedural memory — learned workflows/preferences.
- Preference memory — user choices and communication preferences.
- Task memory — objectives, plans, artifacts, approvals, failures, verification.

Provider adapters may use local storage, PostgreSQL, Redis, or vector databases such as Qdrant/Pinecone/Chroma. The core contracts remain provider-neutral.

## 7. Proactive operation
Saphira may wake from:
- scheduled jobs;
- calendar events;
- monitored system/business events;
- integration webhooks;
- task deadlines;
- explicit user-defined triggers.

Proactive actions must respect the same autonomy policy as interactive requests.

## 8. Coding and self-debugging
The Developer agent can generate and test code through an isolated sandbox. Self-modification of production Saphira is never implicit: proposed code changes must pass tests, security checks, and an approval/deployment policy before production mutation.

## 9. Security boundaries
- Secrets stay outside source control.
- Tool scopes are explicit and revocable.
- Every real-world action is auditable.
- Destructive and financial operations require approval.
- Sandboxed code execution is isolated from production credentials.
- Agent outputs are untrusted until verified.

## 10. Competitive parity + 1% edge
Saphira implements feature parity with category leaders and targets a **1% product edge** on the unified loop (not on isolated leaderboard claims):

| Leader | Category | Saphira edge |
|--------|----------|--------------|
| OpenAI | Conversational versatility, multimodal, agents | One identity + audit + memory |
| Anthropic | Coding, long context, natural writing | Sandbox QA + durable project memory |
| Google | Ecosystem, research, media | Autonomy policy + verified research |
| Microsoft | Enterprise productivity & security | Vendor-neutral control plane + commit gates |
| Meta | Open customization, social AI | Stable runtime over swappable models |
| Perplexity | Cited live research | Research artifacts in episodic/task memory |
| xAI | Live social signal, direct STEM | Tool-grounded STEM + scoped social actions |
| DeepSeek | Cost-efficient reasoning/coding | Cost-aware routing without dropping QA |

Full matrix: `docs/SAPHIRA_COMPETITIVE_EDGE.md`. Capability keys: `src/core/saphira_capability_catalog.py`. Directive: `src/core/saphira_competitive_directive.py`.

## 11. Product principle
**Talk to Saphira. Saphira thinks. Saphira delegates. Saphira executes. Saphira verifies. Saphira remembers — and aims to be 1% better at the whole loop than any single-category leader.**

Agents are implementation details, not separate assistants presented to the user.
