# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Camera surface for mobile / desktop nodes — list, snap, clip.

Real implementations live in the iOS/Android companion apps and feed
Aura (perception) + the dual-pipeline persona.
"""

from __future__ import annotations

from typing import Any, Dict


async def handle(node, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    action = command.split(".", 1)[-1] if "." in command else command

    if action == "list":
        # Simulated device list
        return {
            "status": "ok",
            "action": "camera.list",
            "devices": [
                {"id": "front-0", "name": "Front Camera", "position": "front", "deviceType": "wide"},
                {"id": "back-0", "name": "Back Camera", "position": "back", "deviceType": "wide"},
            ],
            "simulation": True,
            "message": f"Camera devices listed for node {node.name}.",
        }

    if action == "snap":
        facing = params.get("facing", "front")
        max_width = params.get("maxWidth", 1600)
        quality = params.get("quality", 0.9)
        return {
            "status": "ok",
            "action": "camera.snap",
            "facing": facing,
            "format": "jpg",
            "maxWidth": max_width,
            "quality": quality,
            "base64": None,  # real node returns compressed jpg base64
            "width": max_width,
            "height": int(max_width * 0.75),
            "simulation": True,
            "message": f"Photo snap ({facing}) would capture on {node.name}.",
            "feeds_to": "aura",  # perception agent
        }

    if action == "clip":
        facing = params.get("facing", "front")
        duration_ms = min(int(params.get("durationMs", 3000)), 60000)
        include_audio = params.get("includeAudio", True)
        return {
            "status": "ok",
            "action": "camera.clip",
            "facing": facing,
            "durationMs": duration_ms,
            "format": "mp4",
            "hasAudio": include_audio,
            "base64": None,
            "simulation": True,
            "message": f"{duration_ms}ms clip ({facing}) would record on {node.name}.",
            "feeds_to": "aura",
        }

    return {
        "status": "error",
        "error": "UNKNOWN_CAMERA_ACTION",
        "message": f"Unsupported camera action: {action}",
    }
