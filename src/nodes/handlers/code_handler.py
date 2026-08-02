# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Headless / VS Code node handlers — code, repos, tests, PRs, local envs.

These are structured stubs that Agent Zero can already call. Real nodes
(CLI process or VS Code extension) replace the simulation with local
filesystem / git / test-runner access.
"""

from __future__ import annotations

from typing import Any, Dict
import os


async def handle(node, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    action = command.split(".", 1)[-1] if "." in command else command

    if action == "read":
        path = params.get("path", ".")
        return {
            "status": "ok",
            "action": "code.read",
            "path": path,
            "note": "Real headless node would stream workspace files here.",
            "simulation": True,
            "message": f"Read request for '{path}' accepted on node {node.name}.",
        }

    if action == "write":
        path = params.get("path")
        content = params.get("content", "")
        if not path:
            return {"status": "error", "error": "MISSING_PATH", "message": "path required"}
        return {
            "status": "ok",
            "action": "code.write",
            "path": path,
            "bytes": len(content.encode("utf-8")),
            "simulation": True,
            "message": f"Write staged for '{path}' on node {node.name}.",
        }

    if action == "exec":
        cmd = params.get("cmd") or params.get("command")
        cwd = params.get("cwd", ".")
        if not cmd:
            return {"status": "error", "error": "MISSING_CMD"}
        return {
            "status": "ok",
            "action": "code.exec",
            "cmd": cmd,
            "cwd": cwd,
            "simulation": True,
            "message": f"Exec queued: {cmd}",
            "stdout_preview": f"[simulated] ran `{cmd}` in {cwd}",
        }

    if action == "test":
        suite = params.get("suite", "pytest")
        return {
            "status": "ok",
            "action": "code.test",
            "suite": suite,
            "simulation": True,
            "message": f"Test suite '{suite}' would run on node {node.name}.",
        }

    if action == "pr":
        title = params.get("title", "Saphira automated PR")
        branch = params.get("branch", "saphira/auto")
        return {
            "status": "ok",
            "action": "code.pr",
            "title": title,
            "branch": branch,
            "simulation": True,
            "message": f"PR '{title}' would be opened from {branch}.",
        }

    if action == "env":
        # Local database / server environment scaffolding
        env_name = params.get("name", "saphira-dev")
        services = params.get("services", ["postgres", "redis"])
        return {
            "status": "ok",
            "action": "code.env",
            "env_name": env_name,
            "services": services,
            "simulation": True,
            "message": f"Local env '{env_name}' with {services} would be constructed.",
        }

    return {
        "status": "error",
        "error": "UNKNOWN_CODE_ACTION",
        "message": f"Unsupported code action: {action}",
    }
