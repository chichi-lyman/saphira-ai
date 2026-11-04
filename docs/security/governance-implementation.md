# Saphira Core Governance Implementation

## Code delivered in this branch

- Password registration/authentication helpers using PBKDF2-HMAC-SHA256, opaque session tokens, hashed-token storage, expiry, revocation, and atomic refresh rotation.
- RFC 6238 administrator TOTP with one-time counter consumption. The secret resolver and counter store must be protected and durable.
- Deny-by-default RBAC, permission catalogue, scoped resource checks, and policy decisions that route privileged permissions to master approval.
- Ed25519 public-key verification, durable key-registry/revocation interfaces, canonical signed command envelopes, and a KMS signer interface.
- Master gateway pins a configured immutable administrator account ID, validates MFA, registered command/action-to-permission mapping, signature algorithm, key ownership, signature, command scope, time window, revocation, command-ID replay, and nonce replay.
- Master override manager records an authorization intent before performing a protected action, then records and verifies the result.
- Master-authorized emergency stop, delegated short-lived agent credentials, and a common execution guard.
- Hash-chained audit events, optional mandatory KMS signatures, atomic append interface, and chain/signature verification.
- Controlled key-rotation service contract.
- Unit tests for account authentication/session rotation, TOTP replay rejection, nonce replay, RBAC/policy denial, and audit tamper detection.

## Production dependencies — must be supplied by the deployment

The code intentionally does not embed a master private key, create a default master identity, or ship development credentials. Production must provision the master administrator by immutable account ID and store public verification keys through a controlled bootstrap process. The private signing key must remain in a KMS/HSM; the application receives signatures from the KMS operation, never the private key.

Production adapters must implement durable, strongly consistent interfaces for account/session records, MFA secrets and used TOTP counters, public-key registry, key revocation, nonce/command-ID consumption, delegated grants, emergency-stop state, and audit events. The audit store must be append-only, independently backed up, and configured with `AuditRecorder(require_signature=True, signer=..., signing_key_id=...)`. The KMS signer must sign both privileged commands and audit-event digests where configured.

The local `InMemoryNonceStore` and `InMemoryAuditStore` are test-only. They are not suitable for multi-worker or production deployments. Key rotation must use a transactional store operation that atomically installs the replacement key and disables the old key; the revocation record and audit event must be retained.

## Integration boundary and current release blockers

The governance modules do not secure an application entry point merely by existing. In particular, the current chat API and existing orchestration/worker paths must be wired to authenticate a trusted principal and call `ExecutionGuard` before any agent, provider, tool, integration, scheduler, or worker execution. Do not trust a role or administrator name supplied in request JSON. The current chat router's visible request model does not itself establish an authenticated user principal, so this integration is still a release blocker.

Do not enable privileged actions until every execution entry point is guarded; durable adapters are deployed; master MFA and KMS signing are configured; key rotation/recovery and emergency stop are exercised; and the adversarial integration suite passes. Missing configuration, failed signature verification, unavailable authorization services, and unavailable replay stores must fail closed.

## Validation status

Tests have been added but must pass in CI before merge. A previous CI revision showed P0 integration passing while broader Python/package/agent workflows failed. Later branch commits changed the implementation and need a fresh completed CI run. This pull request is a code implementation baseline, not a production security certification.
