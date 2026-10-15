"""Atomic score primitives — lowest breakdown of every Tier S metric.

Each competitive score is split into independent, measurable, repairable units.
Agents repair the failing atom, not the whole system.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class AtomicPrimitive:
    id: str
    parent_score: str
    agent_owners: tuple[str, ...]
    target: float | str
    unit: str
    check: str  # human-readable invariant
    repair_hint: str
    severity: str = "high"  # critical | high | medium


ATOMIC_PRIMITIVES: tuple[AtomicPrimitive, ...] = (
    # --- Saphira: Context Retention & Execution Speed ---
    AtomicPrimitive(
        "ctx_write_ack",
        "context_retention",
        ("saphira", "novaaethrea"),
        1.0,
        "bool",
        "Every user turn must be acknowledged into dual_memory within the same request",
        "Re-append turn via dual_memory.append_turn; verify recent_context non-empty",
        "critical",
    ),
    AtomicPrimitive(
        "ctx_recall_hit",
        "context_retention",
        ("novaaethrea", "saphira"),
        0.999,
        "ratio",
        "Recall must return prior durable facts for keys written this session",
        "Promote RAM→durable; rebuild context_pack; reindex if pgvector configured",
        "critical",
    ),
    AtomicPrimitive(
        "ttft_budget",
        "execution_speed",
        ("saphira", "aura", "agent_zero"),
        350.0,
        "ms",
        "Time-to-first-token / first dispatch must stay ≤ 350ms on local path",
        "Force LatencyRouter local_vllm/webgpu; skip non-critical tools on voice path",
        "critical",
    ),
    AtomicPrimitive(
        "ttft_floor",
        "execution_speed",
        ("aura", "agent_zero"),
        180.0,
        "ms",
        "Warm local path target floor ~180ms (aspirational, not hard fail)",
        "Prefetch model; keep FG service warm; reduce cold-start",
        "medium",
    ),
    # --- NovaReign / NovaAethrea: Efficiency & routing ---
    AtomicPrimitive(
        "route_latency",
        "system_efficiency",
        ("novareign", "novaaethrea", "orchestrator"),
        0.02,
        "ms",
        "Pure route decision (no I/O) must complete under 1ms wall typically",
        "Keep ExcellenceRouter keyword tables in-memory; no network in decide()",
        "high",
    ),
    AtomicPrimitive(
        "efficiency_ratio",
        "system_efficiency",
        ("novareign", "novaaethrea"),
        0.998,
        "ratio",
        "Successful dispatches / total dispatches ≥ 99.8% design target",
        "SelfRepairEngine retry with backoff; quarantine poisoned payloads",
        "high",
    ),
    # --- Aura / Agent Zero: Loop prevention ---
    AtomicPrimitive(
        "loop_block",
        "loop_prevention",
        ("aura", "agent_zero", "cipher"),
        1.0,
        "bool",
        "Identical (session, intent_hash, agent) cycles must be blocked 100%",
        "LoopGuard.reject; transition to RECONCILIATION_REQUIRED",
        "critical",
    ),
    AtomicPrimitive(
        "state_legal",
        "loop_prevention",
        ("agent_zero", "novareign"),
        1.0,
        "bool",
        "Only legal ExecutionState transitions allowed",
        "Use core.hardening.execution_state.transition; never skip states",
        "critical",
    ),
    # --- Agent Two / Cipher: Privacy ---
    AtomicPrimitive(
        "zero_egress_secrets",
        "privacy_isolation",
        ("cipher", "agent_two", "saphira"),
        0.0,
        "leaks",
        "Zero secrets/PII may leave device after PrivacyFilter",
        "Re-run PrivacyFilter; drop outbound if still dirty",
        "critical",
    ),
    AtomicPrimitive(
        "ledger_append_only",
        "privacy_isolation",
        ("cipher",),
        1.0,
        "bool",
        "Execution ledger must remain append-only",
        "Refuse mutate/delete on ledger events; rotate to new segment only",
        "critical",
    ),
    # --- Scholar / Apex / Lexis / Instinct: Multi-agent task accuracy ---
    AtomicPrimitive(
        "task_complete",
        "task_completion",
        ("scholar", "apex", "lexis", "instinct", "agent_two"),
        0.994,
        "ratio",
        "Multi-agent tasks must reach terminal success ≥ 99.4% design target",
        "Re-plan with Scholar; narrow tool set; escalate to human only on policy deny",
        "high",
    ),
    AtomicPrimitive(
        "routing_accuracy",
        "task_completion",
        ("saphira", "orchestrator"),
        0.994,
        "ratio",
        "Auto-routed agent must match task specialty",
        "Re-run ExcellenceRouter with prefer=pillars; adjust keyword map",
        "high",
    ),
)


def decompose_score(parent_score: str) -> list[AtomicPrimitive]:
    return [p for p in ATOMIC_PRIMITIVES if p.parent_score == parent_score]


def primitives_for_agent(agent: str) -> list[AtomicPrimitive]:
    a = agent.lower()
    return [p for p in ATOMIC_PRIMITIVES if a in p.agent_owners]
