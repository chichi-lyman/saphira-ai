# Saphira Core Governance Implementation

## Implemented in this branch

- Standard account password verification using PBKDF2-HMAC-SHA256 and opaque session-token helpers.
- RFC 6238 TOTP step-up verification for administrator authentication.
- Deny-by-default RBAC, a permission catalogue, and privileged-action policy decisions.
- Ed25519 public-key verification and a key registry/revocation interface.
- Canonical signed command envelopes and a KMS signer protocol. No private key material is stored in this repository.
- Master command gateway enforcing administrator identity, MFA, key trust, signature, scope, expiry, revocation, and one-time nonce consumption.
- Override manager, master-authorized emergency stop, scoped delegated agent grants, and execution guard.
- Hash-chained audit events and chain verification.

## Required production adapters and rollout gates

The in-memory key registry, revocation registry, nonce store, delegated-grant store, emergency-stop store, and audit store are development/test adapters only. Before production, replace them with durable, strongly consistent services. Use a managed KMS/HSM signer, database-backed key lifecycle and revocation, atomic nonce consumption with TTL, centrally revocable delegated credentials, an independently backed-up append-only audit sink, and a durable emergency-stop latch.

The application must call ExecutionGuard at every API, worker, agent, provider, integration, and scheduler execution boundary. The repository modules do not automatically secure call sites that have not been wired to the guard. Master administrator identity and trusted public keys must be provisioned through a controlled bootstrap procedure; do not infer master status from a display name or a user-editable role.

Do not enable privileged operations until the KMS signer, MFA secret store, persistent stores, replay protection, audit retention, key rotation/recovery, and integration tests have passed security review. Missing configuration or unavailable verification dependencies must fail closed.

## Test and validation status

Unit tests are included for RBAC denial, privileged-action policy decisions, audit-chain tamper detection, and malformed TOTP rejection. These tests have not been executed in this branch-creation operation. CI results and full application integration remain release gates.
