# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Device / notifications / system surfaces for mobile & headless nodes.
"""

from __future__ import annotations

from typing import Any, Dict


async def handle_device(node, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    action = command.split(".", 1)[-1] if "." in command else command

    if action == "location":
        return {
            "status": "ok",
            "action": "device.location",
            "lat": None,
            "lon": None,
            "accuracy_m": None,
            "simulation": True,
            "message": f"Location feed would stream from {node.name}.",
        }

    if action == "screen":
        return {
            "status": "ok",
            "action": "device.screen",
            "format": params.get("format", "png"),
            "simulation": True,
            "message": "Screen capture would return base64 frame.",
        }

    return {
        "status": "error",
        "error": "UNKNOWN_DEVICE_ACTION",
        "message": f"Unsupported device action: {action}",
    }


async def handle_notifications(node, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    title = params.get("title", "Saphira")
    body = params.get("body") or params.get("message", "")
    return {
        "status": "ok",
        "action": "notifications.send",
        "title": title,
        "body": body,
        "simulation": True,
        "message": f"Native notification would fire on {node.name}: {title}",
    }


async def handle_system(node, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    action = command.split(".", 1)[-1] if "." in command else command

    if action == "exec":
        cmd = params.get("cmd") or params.get("command")
        return {
            "status": "ok",
            "action": "system.exec",
            "cmd": cmd,
            "simulation": True,
            "message": f"Remote system command queued on {node.name} (subject to allowlist).",
        }

    if action == "sms":
        # Android-only, gated
        to = params.get("to")
        body = params.get("body", "")
        if node.node_type.value != "mobile_android":
            return {
                "status": "error",
                "error": "PLATFORM_UNSUPPORTED",
                "message": "SMS only available on Android nodes.",
            }
        return {
            "status": "ok",
            "action": "system.sms",
            "to": to,
            "simulation": True,
            "message": "Background SMS would send (Android, user-gated).",
        }

    if action == "info":
        return {
            "status": "ok",
            "action": "system.info",
            "node": node.to_dict(),
            "message": "Node system info.",
        }

    return {
        "status": "error",
        "error": "UNKNOWN_SYSTEM_ACTION",
        "message": f"Unsupported system action: {action}",
    }
