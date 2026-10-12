# Copyright © 2026 Chelsea Megan Woods
# Saphira AI — Controlled Self-Reflection & Candidate Build Workflow
#
# Safe recovery cycle: capture → diagnose → stage candidate → isolated test →
# human-approved promotion. Never hot-reloads arbitrary modules into the live
# process. Aligns with evolution_engine and self_healing invariants.
#
# Pipeline remains fixed:
#   Saphira (intent) → Aura (perception) → Agent Two (security) →
#   Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)

from __future__ import annotations

import ast
import json
import logging
import os
import shutil
import subprocess
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LOG = logging.getLogger("saphira.reflection")

ROOT = Path(__file__).resolve().parents[1]
INCIDENT_DIR = ROOT / "runtime_incidents"
CANDIDATE_DIR = ROOT / "runtime_candidates"


def capture_exception(exc: BaseException) -> Path:
    """Persist diagnostic context without environment secrets."""
    INCIDENT_DIR.mkdir(parents=True, exist_ok=True)
    incident_id = str(uuid.uuid4())
    path = INCIDENT_DIR / f"{incident_id}.json"

    record = {
        "incident_id": incident_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exception_type": type(exc).__name__,
        "message": str(exc)[:2000],
        "traceback": "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )[-12000:],
        "status": "CAPTURED",
    }
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    LOG.error("Incident captured: %s", incident_id)
    return path


def validate_python(candidate: Path) -> None:
    """Syntax-check only; this is not a security sandbox."""
    source = candidate.read_text(encoding="utf-8")
    ast.parse(source, filename=str(candidate))


def test_candidate(candidate: Path, test_file: Path) -> None:
    """Run tests in a separate process with a timeout."""
    validate_python(candidate)

    result = subprocess.run(
        [
            sys.executable, "-I", "-m", "pytest",
            "-q", str(test_file),
        ],
        cwd=str(candidate.parent),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        env={
            "PATH": str(Path(sys.executable).parent),
            "PYTHONIOENCODING": "utf-8",
        },
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Candidate tests failed:\n" + result.stdout[-4000:]
            + result.stderr[-4000:]
        )


def stage_candidate(
    generated_file: Path,
    module_name: str,
    test_file: Path,
) -> Path:
    """
    Stage an LLM-generated module for review.
    Never overwrites the live module.
    """
    if not module_name.isidentifier():
        raise ValueError("Invalid module name")

    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    candidate = CANDIDATE_DIR / f"{module_name}_candidate.py"
    shutil.copyfile(generated_file, candidate)

    try:
        test_candidate(candidate, test_file)
    except Exception as exc:
        capture_exception(exc)
        raise

    return candidate


def promote_candidate(
    candidate: Path,
    live_module: Path,
    *,
    approved: bool = False,
) -> None:
    """
    Promotion requires explicit approval.
    Use an atomic deployment/symlink switch or process restart in production.
    """
    if not approved:
        raise PermissionError("Human approval is required for promotion")

    validate_python(candidate)
    live_module.parent.mkdir(parents=True, exist_ok=True)

    backup = live_module.with_suffix(live_module.suffix + ".bak")
    if live_module.exists():
        shutil.copy2(live_module, backup)

    # os.replace is atomic on the same filesystem, but does not make
    # a running interpreter safely reload the replaced module.
    os.replace(candidate, live_module)
    LOG.info("Promoted candidate %s -> %s (backup at %s)", candidate, live_module, backup)


if __name__ == "__main__":
    try:
        raise RuntimeError("Demonstration failure: agent timeout")
    except Exception as exc:
        print("Incident written to:", capture_exception(exc))
