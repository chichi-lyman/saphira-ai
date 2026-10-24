# Nova Umbrella Autonomous Engineering Workbench

**Product:** Saphira AI  
**Ecosystem:** Nova Umbrella  
**Owner:** Chelsea Megan Woods  
**Status:** Architecture and implementation contract; code execution and external actions remain disabled until implemented, tested, and explicitly configured.

## Purpose

Introduce a governed engineering workbench in Saphira AI that can assist with isolated data analysis, multi-file application scaffolding, repository refactoring and security reviews, and structured data pipelines. The workbench should orchestrate tools through existing Saphira Core/provider contracts rather than create a second model router.

The assistant may plan and propose multi-step work, execute permitted sandbox tasks, inspect results, correct failures within bounded limits, and produce auditable artifacts. It must never represent a proposed or simulated action as executed.

## User-facing capability areas

1. **Data Lab**
   - Ingest user-provided CSV, JSON, JSONL, XML, TXT, and supported document files.
   - Profile schemas, detect encoding and malformed rows, normalize fields, deduplicate records, validate types, and report rejected rows.
   - Use isolated Python execution for analysis and deterministic transformations.
   - Generate summary tables and charts when appropriate; export cleaned data and a transformation report.
   - Enforce file-size, row-count, CPU, memory, execution-time, and output-size limits.

2. **App Builder**
   - Convert a feature brief into an architecture plan, file manifest, implementation checklist, and dependency map.
   - Scaffold multi-file React/TypeScript, Node.js, and Python applications with validation, configuration, tests, and error handling.
   - Reuse approved templates and pinned dependency policies.
   - Generate patches on a feature branch; do not deploy or modify production automatically.
   - Provide setup instructions, environment-variable examples, and tests without embedding secrets.

3. **Repository Refactor & Security Review**
   - Inspect repository files the authenticated user is authorized to access.
   - Map entry points, dependencies, data flow, API boundaries, and duplicate abstractions.
   - Detect likely secrets, unsafe deserialization, injection risks, weak authorization, dependency issues, insecure defaults, and missing tests.
   - Classify findings by severity and confidence with file/line evidence where available.
   - Propose minimal, reviewable patches and regression tests.
   - Require explicit approval before writes to protected branches, destructive changes, or deployment.

4. **Data Pipeline Studio**
   - Parse JSON/XML and structured or semi-structured text using bounded parsers and explicit schemas.
   - Extract entities from documents with provenance and confidence labels; treat extracted text as untrusted input.
   - Draft relational schemas and database migrations with primary keys, foreign keys, indexes, constraints, and rollback strategy.
   - Validate generated output against schemas and test fixtures before export or application.
   - Never apply a production migration without an explicit approval step and a verified backup/rollback plan.

5. **Engineering Agent**
   - Build a task plan with preconditions, expected artifacts, tool permissions, and stop conditions.
   - Run bounded inspect → plan → patch → test → analyze failure → patch loop.
   - Cap retries, elapsed time, token/cost budgets, and changed-file count.
   - Preserve logs and test results; stop and report when the same failure repeats or confidence is insufficient.
   - Separate read, sandbox-write, branch-write, external-network, and production privileges.

## Runtime architecture

Use the existing Saphira Core orchestration, provider registry, configuration, authentication, and governance contract.

```text
Saphira UI (Chats / Memories / Tools / Settings)
  └─ Engineering Workbench
      ├─ Task Planner and typed task manifest
      ├─ Policy / Approval Gate
      ├─ Existing Saphira Core model gateway
      ├─ Tool adapters
      │   ├─ Sandboxed Python runner
      │   ├─ File parser and artifact exporter
      │   ├─ Repository reader / patch generator
      │   ├─ Test and lint runner
      │   └─ Schema and migration validator
      ├─ Bounded correction controller
      └─ Audit / usage / artifact ledger
          └─ Configured persistence layer
```

No parallel provider router should be introduced. Existing provider calls remain disabled unless credentials and feature flags are configured.

## Suggested typed task envelope

```json
{
  "task_id": "server-generated-uuid",
  "task_type": "data_cleaning",
  "status": "proposed",
  "requested_by": "authenticated-user-id",
  "scope": {
    "input_artifact_ids": [],
    "repository": null,
    "allowed_paths": [],
    "output_formats": ["csv", "json", "report"]
  },
  "limits": {
    "max_attempts": 3,
    "timeout_seconds": 60,
    "max_output_bytes": 20000000,
    "network_access": false
  },
  "approval": {
    "required": false,
    "status": "not_required"
  },
  "artifacts": [],
  "audit_event_ids": []
}
```

The envelope is an illustrative contract. Validate all fields at runtime, generate IDs server-side, and do not trust user-supplied permissions or limits.

## Security and isolation requirements

- Run untrusted code in an ephemeral container or equivalent hardened sandbox with no host filesystem access, no privileged mode, non-root identity, read-only base image, restricted syscalls, CPU/memory/PID/time quotas, and process cleanup.
- Default to no network access. Use explicit allowlists and approval for any task that requires network access.
- Mount only the task's scoped input and output directories. Do not expose repository credentials, cloud metadata endpoints, environment secrets, or other tenants' data.
- Treat repository contents, uploaded documents, model output, and generated code as untrusted. Ignore instructions embedded in retrieved files that attempt to override system policies or expand permissions.
- Scan uploads and generated artifacts where appropriate. Enforce MIME/type checks, archive traversal protection, path normalization, and output path containment.
- Use tenant-scoped authorization on every read and write. Apply least privilege and audit access denials.
- Keep API keys server-side and redact secrets from logs and reports.
- Require approval for branch writes, pull requests, external messages, deployments, production database changes, paid actions, and destructive operations.
- Use idempotency keys for retried external operations; never retry an irreversible action blindly.
- Define retention/deletion policy for uploaded files, temporary environments, logs, and generated artifacts.

## Governance lifecycle

`PROPOSE → VALIDATE → AUTHORIZE → RESERVE → EXECUTE → VERIFY → COMMIT / ROLLBACK`

- **PROPOSE:** summarize intent, scope, planned operations, and expected outputs.
- **VALIDATE:** check schema, paths, limits, dependencies, and policy.
- **AUTHORIZE:** apply ALLOW / REQUIRE_APPROVAL / DENY.
- **RESERVE:** allocate bounded compute, usage budget, and temporary storage.
- **EXECUTE:** run only authorized tools in the isolated environment.
- **VERIFY:** run tests, output validation, and security checks.
- **COMMIT / ROLLBACK:** export artifacts or create a branch patch only after checks; remove temporary state on failure.

## Telemetry

Record task type, actor/tenant ID, policy decision, provider/tool identifier, duration, exit status, retry count, test outcomes, resource usage, artifact hashes, and approval events. Avoid logging secrets, raw sensitive document content, or unrestricted prompts. Expose operational metrics through existing telemetry conventions where available.

## Feature flags

Keep these false until the associated implementation, tests, and infrastructure are verified:

- `engineering_workbench_enabled`
- `python_sandbox_enabled`
- `data_lab_enabled`
- `app_builder_enabled`
- `repository_audit_enabled`
- `patch_generation_enabled`
- `database_migration_generation_enabled`
- `external_network_tools_enabled`

A feature flag does not replace authorization or approval.

## Minimum acceptance criteria

- [ ] UI exposes the capability through the existing Tools area without creating a second assistant identity.
- [ ] Every task has a typed manifest, scope, bounded resource budget, status, and audit trail.
- [ ] Python runs in an isolated, ephemeral environment with network disabled by default.
- [ ] Data cleaning reports input/output counts, transformations, validation failures, and rejected rows.
- [ ] App Builder creates a reproducible file manifest and tests; no production deployment occurs by default.
- [ ] Repository audit provides evidence-based findings and does not write to the repository during read-only review.
- [ ] Patch application occurs only in a scoped feature branch after approval.
- [ ] Generated SQL migrations are linted/validated and include rollback notes; production execution requires approval.
- [ ] Self-correction has hard retry, time, cost, and file-change limits.
- [ ] Authorization tests prove cross-tenant data isolation and blocked privilege escalation.
- [ ] Tests cover timeout, memory/output limits, malicious paths, prompt injection in files, secret redaction, failed provider calls, rollback, and approval gates.
- [ ] Missing provider configuration reports unavailable; it never returns fabricated success.
- [ ] CI runs formatting, lint, type checks, unit tests, and security checks before merge.

## Phased delivery

**Phase 1 — contracts and safe foundation:** task schemas, feature flags, permission model, audit events, artifact metadata, and policy tests.

**Phase 2 — Data Lab:** isolated Python runner, parsers, validation, CSV/JSON export, and deterministic tests.

**Phase 3 — Engineering Agent and App Builder:** task planning, bounded test-and-correction loop, template scaffolding, branch-based patch flow.

**Phase 4 — Repository security and pipelines:** evidence-based audit reports, structured extraction, migration generation and validation.

**Phase 5 — app integration and operations:** UI, persistence, telemetry dashboards, authenticated smoke tests, deployment after review.

## Current status disclaimer

Adding this specification does not itself implement the runner, UI, migrations, repository adapters, security scanner, or production workflow. Mark each capability as planned until code, tests, and runtime configuration verify it.
