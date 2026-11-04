# RFC-0001: Sovereign Agent State Synchronization & Data Privacy Protocol (SASP-1)

- **Status:** Experimental proposal
- **Version:** 1.0-draft
- **Normative language:** MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY define requirements in this draft.

## Abstract
SASP-1 defines interoperable boundaries for sovereign agent state synchronization: deterministic event identity, cryptographic node authentication, scoped state exchange, conflict handling, and privacy for local or air-gapped systems. Integrity does not establish truth.

## 1. Architecture Model — Deterministic DAG Routing
Nodes represent authenticated agents/services. Immutable events contain event ID, actor identity, parent event IDs, policy version, timestamp, payload digest, and signature. Implementations MUST canonically serialize signed fields. Routing MUST be deterministic for a fixed policy, input, and declared capability set. Model output is not presumed deterministic; consequential output digests and model/configuration metadata SHOULD be recorded.

DAG edges represent causal parentage. Implementations MUST reject cycles and preserve ancestry. Conflict resolution MUST be explicit; last-write-wins MUST NOT silently override authorization or provenance conflicts.

## 2. Cross-Node Cryptographic Identity Verification
Each node MUST have a distinct key pair. Peers MUST authenticate through a trusted certificate or pinned public key and verify signatures over canonical envelopes. Key rotation, revocation, and trust-root distribution MUST be deployment-defined.

A signature proves possession/use of a signing key, not human identity, payload truth, or authorization. Authorization MUST be checked separately. Replay resistance MUST use event IDs/nonces, causal parents, and validity windows where clocks are available.

## 3. Data Sovereignty Guarantees
Nodes MUST enforce owner policy before export. Exchange MUST be purpose-bound, capability-scoped, and data-minimized. Private local state MUST remain local unless policy permits transfer. Implementations SHOULD support classification, retention, encryption, deletion/export controls, provenance receipts, log redaction, and user-visible transfer records.

Sovereignty depends on operator, host, key custody, and policy assumptions; these MUST be documented.

## 4. Threat Model and Air-Gapped Security Constraints
Threats include compromised peers, replay, forged payloads, unauthorized export, stale policy, compromised credentials, partitions, and malformed input. Nodes MUST validate schema, limits, signature, policy version, ancestry, and replay state before applying state. Unknown peers MUST be denied by default.

Air-gapped deployments MUST distribute trust roots, revocations, and policy updates through authenticated offline procedures. A compromised node can lie about its observations. Hashes/signatures make tampering detectable but do not establish truth. High-assurance deployments SHOULD independently anchor ledger checkpoints.

## 5. State Synchronization
Synchronization MUST be incremental and idempotent. Events MUST be applied at most once. Missing parents MUST be requested or quarantined; ancestry MUST NOT be invented. Policy version conflicts MUST pause protected writes pending reconciliation. During partitions, locally authorized work MAY continue, but global consistency MUST NOT be claimed before reconciliation.

## 6. Privacy and Operational Security
Private keys, tokens, and raw secrets MUST NOT enter event payloads. Sensitive fields SHOULD be end-to-end encrypted for intended recipients. Logs SHOULD record decision metadata instead of unnecessary raw data.

## 7. Conformance
Tests SHOULD cover canonicalization, signature verification, replay rejection, duplicate idempotency, DAG cycle rejection, policy mismatch, export scope, partition reconciliation, and offline trust updates.

## 8. Security Considerations
Cryptography, deterministic routing, and local execution are controls, not guarantees. Independent security review is required before production. This is an experimental draft, not an adopted IETF RFC or W3C Recommendation.
