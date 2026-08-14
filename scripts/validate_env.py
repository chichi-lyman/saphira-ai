#!/usr/bin/env python3
"""
Saphira AI — offline environment validation.

Usage:
  python scripts/validate_env.py
  python scripts/validate_env.py --strict
  python scripts/validate_env.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure repository root is on sys.path when run as a script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Saphira environment variables")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require at least one LLM provider API key",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print validation report as JSON",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT / ".env.local", override=False)

    from src.config.settings import validate_environment
    from pydantic import ValidationError

    try:
        settings = validate_environment(strict=args.strict)
    except ValidationError as exc:
        print("FAIL: environment validation error", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    report = settings.validation_report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("OK: environment validated")
        for key, value in report.items():
            print(f"  {key}: {value}")
        if not report["llm_provider_configured"]:
            print(
                "  note: no LLM provider key set (OPENAI_API_KEY / GEMINI_API_KEY / XAI_API_KEY); "
                "chat may be limited until configured."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
