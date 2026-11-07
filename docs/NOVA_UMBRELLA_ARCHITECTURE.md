# Nova Umbrella Ecosystem Architecture

**Status:** Architecture specification / implementation baseline  
**Root authority:** Chelsea Megan Woods (a.k.a. Chelsea Megan Lyman)  
**System:** Saphira AI + Nova Umbrella  
**Policy principle:** Agents may reason, coordinate, optimize, and recover only inside explicitly granted capability and resource boundaries. They cannot redefine those boundaries.

## 1. Governance and identity anchor

The ecosystem uses a single-root-authority governance model. The root identity is represented operationally by a public-key trust anchor; a display name is not an authentication credential.

The Genesis Policy must be stored and versioned outside ordinary agent-writable execution paths. Agents and runtime services must not be able to:
- change the root identity or trusted public key;
- grant or elevate their own permissions;
- disable approval requirements or security telemetry;
- bypass authorization windows or policy checks; or
- replace the active governance policy without an authorized, auditable change.

Use a hardware-backed signing key where supported. Biometric verification may unlock use of that key, but is not itself a cryptographic signature. Never store private signing keys in source control, application configuration, logs, or agent context.

## 2. Architecture layers and registry

| Layer | Components | Responsibilities |
|---|---|---|
| 1 — Interface | Saphira AI | User interaction, command intake, wake-word capture where supported, display of action/approval status. UI preference: white (#FFFFFF), direct language, minimal jargon. |
| 2 — Cognitive core | NovaReign, Context Engine | Task planning, structured payload processing, context and memory retrieval, resource planning, agent coordination. |
| 3 — Defensive perimeter | Nginx Gateway, Aura | Authentication, request validation, policy enforcement, security telemetry, PII anomaly detection, rate limits, and network filtering. |
| 4 — Private vault | Agent Zero, isolated containers | Code generation, optimization, testing, artifact validation, and controlled execution in sandboxed environments. |

### Agent capability boundaries

- **Saphira AI:** user-facing command interface; no implicit deployment or root-key authority.
- **NovaReign:** planner/orchestrator; delegates only capabilities authorized for the task.
- **Context Engine:** memory and context lifecycle; access is scoped and auditable.
- **Aura:** defensive monitoring and policy evaluation; cannot grant itself root authority.
- **Agent Zero:** sandboxed coding and optimization; cannot deploy boundary-changing code without approval.
- **Other agents:** unique identities, least-privilege capabilities, bounded inputs/outputs, and explicit time/resource limits.

## 3. Decentralized orchestration and resilience

Tier Six orchestration may coordinate authenticated nodes over a private mesh. Peer-to-peer coordination does not confer peer-to-peer root authority. Each node must authenticate its peer, validate the task envelope, and enforce its own local policy.

Resilience requirements:
- isolate individual subtask/provider failures;
- apply bounded retries with exponential backoff and jitter;
- use circuit breakers for unavailable providers;
- preserve successful independent results;
- reassign work only to authorized agents;
- record partial completion and failure reasons;
- fail closed for protected actions when authorization cannot be verified.

A missing provider must not crash unrelated work. A denied subtask must not be retried as a way to evade its denial.

## 4. Self-optimization lifecycle

All generated changes begin in an isolated sandbox with restricted filesystem, network, CPU, memory, and runtime. Changes must pass unit, integration, security, and policy checks before promotion.

Lifecycle:

`PROPOSE → ISOLATE → VALIDATE → AUTHORIZE → DEPLOY → VERIFY → COMMIT`

Any failure leads to rejection or rollback. Changes to root identity, authorization policy, security boundaries, credentials, data migration, or production deployment require root approval. No agent may approve its own high-risk proposal.

## 5. Authorization escrow

High-risk actions are held pending an explicit root-user approval bound to:
- action and target resource;
- exact artifact/version or content digest;
- requested capabilities and scope;
- relevant data movement;
- expiry time and one-time nonce; and
- policy version and audit correlation ID.

Approval must be cryptographically verifiable and single-use. Material changes to the proposal invalidate prior approval. A biometric handshake is a user-authentication mechanism only when implemented through a trusted platform authenticator; the server must verify the resulting signed challenge.

## 6. Communication constraints

User-facing output must be calm, direct, and functional. Avoid emotional mimicry, intimacy cues, filler, marketing language, and needless jargon. Explain action status, partial failures, required approval, and recovery outcome plainly.

## 7. Security implementation notes

- Nginx's 444 behavior can close an unwanted connection without a response; it is not authentication or authorization.
- Use TLS and mutual TLS for service-to-service traffic where applicable.
- Validate schemas and payload sizes at every trust boundary.
- Use least privilege, secret management, encryption in transit/at rest, and tamper-evident audit logs.
- Treat PII detection as a monitoring/control layer, not a substitute for access control or data minimization.
- Context-window size (including a proposed two-million-token target) is a model/provider capacity requirement, not a security property. Verify model support and budget context explicitly.
- The private mesh and self-healing behavior must not depend on an external centralized orchestration server, but trust policy and revocation rules must remain consistent and verifiable.

## 8. Acceptance criteria

1. Agents cannot change the root trust anchor or policy through ordinary tool access.
2. Every protected operation has an authorization decision and correlation ID.
3. Unapproved boundary-changing actions remain in escrow.
4. Approval is bound to the exact action/artifact, expires, and cannot be replayed.
5. Missing providers and individual rejections result in bounded partial failure, not process-wide crashes.
6. Sandbox network and filesystem access are denied by default.
7. Failed validation or deployment health checks trigger rollback.
8. Audit records capture actor, action, target, policy version, decision, approval reference, and outcome without logging secrets.
9. Tests cover deny, approval-required, expiry, replay, provider outage, and rollback paths.

**Important:** This document specifies the required architecture and controls. A documented requirement is not proof that each control is already active in the running deployment; runtime enforcement and tests must be implemented and verified separately.
