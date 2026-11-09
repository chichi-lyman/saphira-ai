# Frontier Execution Layer — Saphira Edge ↔ Nova Umbrella

**© 2026 Chelsea Megan Woods**  
**System:** Saphira AI / Nova Umbrella  
**Related:** [UNSOLVED_AI_FRONTIERS.md](./UNSOLVED_AI_FRONTIERS.md)

This layer implements concrete engineering tracks against the five unsolved frontiers:
continual learning (O-LoRA), reliability (formal verification), embodiment (edge),
AGI jaggedness (multi-agent + simulation hooks), and energy (sparse/edge routing).

## Components

| Path | Role |
|------|------|
| `src/frontier/memory/saphira_olora_memory.py` | FastAPI O-LoRA zero-drift adapters + `/v1/verify/formal` + `/ws/verify` |
| `src/frontier/verification/symbolic_verifier_formal.py` | Process-2 SymPy + Z3 + AST dual-process verifier |
| `src/frontier/bridge/saphira_nova_bridge.py` | Redis pub/sub bridge (edge ↔ NovaReign / Cipher / Lyra) |
| `crates/saphira_symbolic_verifier/` | Rust crate → native `.so` / WASM for µs-latency AST + bounds checks |
| `scripts/setup-termux-edge.sh` | Termux/Android edge bootstrap |
| `deploy/frontier/` | Production Dockerfile, compose (pgvector + Redis), entrypoint |

## Latency tiers

| Path | Typical latency | Footprint |
|------|-----------------|----------|
| Rust WASM / native Process-2 | ~12–45 µs | < 2 MB |
| FastAPI WebSocket formal | ~3–10 ms | network + server |
| FastAPI REST formal (SymPy/Z3) | ~8–25 ms | full solver stack |

## Pipeline placement

```
Saphira (intent) → Aura → Agent Two → Nova Reign
                              │
                    Formal verify gates (Process 2)
                              │
                    NovaAethrea (memory / O-LoRA ledger)
                              │
                    Agent Zero / Edge (Termux, Flutter, actuators)
```

Governance never bypassed: high-stakes outputs still require CommercialAuthorityPolicy
and approval gates even after formal proofs pass.

## Quick start (local)

```bash
# Edge / server
cd deploy/frontier && docker compose up --build -d

# Termux
bash scripts/setup-termux-edge.sh

# Rust microsecond verifier
cd crates/saphira_symbolic_verifier && cargo build --release
```

## Status honesty

These modules are **research-grade production scaffolds**: real APIs, real AST/SMT
gates, real edge packaging. They do **not** claim solved AGI, solved continual
learning at foundation-model scale, or brain-watt efficiency. Advance claims only
when evaluation criteria in UNSOLVED_AI_FRONTIERS.md are met.
