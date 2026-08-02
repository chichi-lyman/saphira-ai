# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Canvas node handlers — interactive dashboards, visual briefings, A2UI-style surfaces.
"""

from __future__ import annotations

from typing import Any, Dict


async def handle(node, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    action = command.split(".", 1)[-1] if "." in command else command

    if action == "present":
        target = params.get("target") or params.get("url") or "about:blank"
        return {
            "status": "ok",
            "action": "canvas.present",
            "target": target,
            "simulation": True,
            "message": f"Canvas on {node.name} would present {target}.",
        }

    if action == "navigate":
        url = params.get("url") or params.get("target")
        return {
            "status": "ok",
            "action": "canvas.navigate",
            "url": url,
            "simulation": True,
            "message": f"Canvas navigating to {url}.",
        }

    if action == "eval":
        js = params.get("js") or params.get("javaScript") or ""
        return {
            "status": "ok",
            "action": "canvas.eval",
            "js_preview": js[:120],
            "result": None,
            "simulation": True,
            "message": "JS eval would run in the canvas WebView.",
        }

    if action == "snapshot":
        fmt = params.get("format", "png")
        return {
            "status": "ok",
            "action": "canvas.snapshot",
            "format": fmt,
            "base64": None,
            "simulation": True,
            "message": f"Snapshot ({fmt}) would be captured from canvas.",
        }

    if action == "a2ui":
        # Agent-to-UI push (OpenClaw A2UI v0.8 style)
        text = params.get("text")
        payload = params.get("jsonl") or params.get("payload")
        return {
            "status": "ok",
            "action": "canvas.a2ui",
            "text": text,
            "has_payload": bool(payload),
            "simulation": True,
            "message": "A2UI surface update pushed to canvas.",
        }

    if action == "dashboard":
        # Mission-control style interactive dashboard
        sources = params.get("sources", ["calendar", "notion", "todos"])
        title = params.get("title", "Saphira Mission Control")
        return {
            "status": "ok",
            "action": "canvas.dashboard",
            "title": title,
            "sources": sources,
            "simulation": True,
            "message": f"Interactive dashboard '{title}' with {sources} would spin up on {node.name}.",
        }

    return {
        "status": "error",
        "error": "UNKNOWN_CANVAS_ACTION",
        "message": f"Unsupported canvas action: {action}",
    }
