#!/usr/bin/env python3
# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""
Generate Saphira avatar stills for each state via Grok Imagine.
Requires XAI_API_KEY. Optional SAPHIRA_AVATAR_MASTER_URL for I2I lock.
"""

from __future__ import annotations

import json
import os
import sys

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.avatar.grok_avatar_service import avatar_service, AvatarState, STATE_PROMPTS


def main():
    print("Saphira Avatar Frame Generator")
    print("Owner: Chelsea Megan Woods")
    print("Status:", json.dumps(avatar_service.status(), indent=2))
    print()

    results = {}
    for state in AvatarState:
        print(f"Generating: {state.value} ...")
        out = avatar_service.generate_frame(state=state)
        results[state.value] = {
            "status": out.get("status"),
            "url": out.get("url"),
            "message": out.get("message"),
        }
        print(f"  -> {out.get('status')} {out.get('url') or out.get('message', '')[:80]}")

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets",
        "avatar",
        "generated_manifest.json",
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nManifest written to {out_path}")


if __name__ == "__main__":
    main()
