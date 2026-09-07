---
name: saphira-improvement
description: Improve and extend the Saphira AI personal assistant including reviewing and refining SKILL.md files persona prompts and agent logic writing or debugging Python scripts for the executive runtime memory engine or tool fabric designing new agent workflows adding vision integration or commerce automation and creating test cases or documentation. Trigger on requests to enhance Saphira improve her agents refine persona update skills debug runtime or expand capabilities.
---

# Saphira Improvement

Assist with development and enhancement of the Saphira AI repository, the Persistent Multimodal Intelligence Operating System by Chelsea Megan Woods under the Nova Umbrella ecosystem.

## Core Principles

- Treat Saphira as a multi-agent executive runtime with the fixed pipeline Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution).
- Preserve the Samantha-style persona (warm, emotionally intelligent, non-robotic, never reveal internal agent names to users).
- Respect copyright and ownership statements already present in the codebase (© 2026 Chelsea Megan Woods).
- Maintain policy-controlled commerce invariants (no autonomous external communication or financial state ownership by the LLM).

## Review and Refine SKILL.md Files, Persona Prompts, and Agent Logic

When refining skills or persona:

1. Load existing SKILL.md or persona files from the repository.
2. Ensure frontmatter follows the agentskills.io format and the strict YAML rules (plain scalar description, no colon-space, no angle brackets).
3. Keep persona prompts in imperative form and enforce the secret-mask rule that hides agent codenames.
4. For agent logic, verify the self-healing pattern and next-agent handoff lists remain consistent with the six-core pipeline.

## Write or Debug Python Scripts for Runtime, Memory, or Tool Fabric

- Prefer async methods matching the existing `safe_run` and `process` patterns in the orchestrator.
- Memory operations should use the PersistentMemoryStore interface (facts, preferences, scenes, history).
- Tool fabric additions must register through the capability registry and respect authorization gates.
- Include type hints, logging via the established logger names, and error recovery that returns recovered_from_failure status when appropriate.

## Design New Agent Workflows

- New agents or workflows must fit as adapters or workers under the Capability Registry.
- Explicitly define status values, avatar-state mappings, and verification steps.
- Document the new flow in a references file if it exceeds a few paragraphs.

## Add Features (Vision Integration, Commerce Automation)

- Vision features should integrate with Aura's perception role and the multimodal boundaries already defined.
- Commerce work must route through CommercialAuthorityPolicy (ALLOW / REQUIRE_APPROVAL / DENY) and the hash-chained audit store.
- Never enable autonomous external messaging or payment activation without signature-verified Stripe events.

## Create Test Cases or Documentation

- Tests should follow the existing pytest style under tests/ and cover authority, audit, and state-machine invariants for commerce.
- Documentation updates belong in ARCHITECTURE.md, DEPLOY.md, or docs/ and must preserve the ownership and trademark notices.

## Working with the Repository

Prefer reading current source before proposing changes. When generating code, output complete, runnable snippets that match the project's copyright header style and Python 3.11+ conventions.

When a change is complete, offer to validate structure or generate a short changelog entry.
