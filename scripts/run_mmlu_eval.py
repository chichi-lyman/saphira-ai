#!/usr/bin/env python3
# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella / Saphira AI — MMLU evaluation CLI

"""Run MMLU against a mock or live agent surface.

Examples:
  python scripts/run_mmlu_eval.py --n-shots 0 --limit 20
  python scripts/run_mmlu_eval.py --n-shots 5 --subjects astronomy,machine_learning
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Allow running from repo root without install
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation import EvaluationRunner


async def mock_model(prompt: str) -> str:
    """Deterministic mock for offline demos — always chooses B."""
    return "B"


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run MMLU evaluation for Saphira / Nova Umbrella agents")
    parser.add_argument("--n-shots", type=int, default=0, choices=range(0, 6), help="0–5 shot prompting")
    parser.add_argument("--limit", type=int, default=None, help="Cap number of questions")
    parser.add_argument("--subjects", type=str, default=None, help="Comma-separated subject filter")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--agent", type=str, default="scholar", help="Logical agent name for logging")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    subjects = None
    if args.subjects:
        subjects = [s.strip() for s in args.subjects.split(",") if s.strip()]

    runner = EvaluationRunner(model_fn=mock_model, agent_name=args.agent)
    result = await runner.run(
        "mmlu",
        n_shots=args.n_shots,
        subjects=subjects,
        limit=args.limit,
        seed=args.seed,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Benchmark : {result.benchmark}")
        print(f"Agent     : {args.agent}")
        print(f"Shots     : {result.n_shots}")
        print(f"Score     : {result.overall_score:.4f} ({result.n_correct}/{result.n_total})")
        print(f"Latency   : {result.latency_ms:.0f} ms")
        print(f"Subjects  : {', '.join(result.subjects) or '(all)'}")
        if result.per_subject:
            print("Per-subject:")
            for s, sc in sorted(result.per_subject.items()):
                print(f"  {s:40s} {sc:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
