# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Saphira Node primitives.

A Node is a companion device or process (headless CLI, VS Code extension,
mobile companion, desktop canvas host) that connects to the Saphira gateway
and exposes a command surface the orchestrator can invoke.

Mirrors the OpenClaw node model while staying native to Saphira's multi-agent
pipeline (Agent Zero for execution, Aura for perception, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid


class NodeType(str, Enum):
    """Deployment style of the node."""

    HEADLESS = "headless"          # CLI / server process (code, pipelines)
    VSCODE = "vscode"              # IDE-aware extension
    CANVAS = "canvas"              # Desktop / web visual surface
    MOBILE_IOS = "mobile_ios"      # iOS companion
    MOBILE_ANDROID = "mobile_android"
    MEDIA = "media"                # Local render / motion-graphics host
    CUSTOM = "custom"


class NodeStatus(str, Enum):
    PENDING = "pending"            # Pairing request awaiting approval
    ONLINE = "online"
    OFFLINE = "offline"
    REJECTED = "rejected"
    BUSY = "busy"


class NodeCapability(str, Enum):
    """Command families a node may expose (OpenClaw-style surfaces)."""

    # Code / software
    CODE_READ = "code.read"
    CODE_WRITE = "code.write"
    CODE_EXEC = "code.exec"
    CODE_TEST = "code.test"
    CODE_PR = "code.pr"
    CODE_ENV = "code.env"

    # Media / creative
    MEDIA_RENDER = "media.render"
    MEDIA_VIZ = "media.viz"
    MEDIA_VIDEO = "media.video"

    # Canvas / UI
    CANVAS_PRESENT = "canvas.present"
    CANVAS_NAVIGATE = "canvas.navigate"
    CANVAS_EVAL = "canvas.eval"
    CANVAS_SNAPSHOT = "canvas.snapshot"
    CANVAS_A2UI = "canvas.a2ui"
    CANVAS_DASHBOARD = "canvas.dashboard"

    # Sensors / physical
    CAMERA_LIST = "camera.list"
    CAMERA_SNAP = "camera.snap"
    CAMERA_CLIP = "camera.clip"
    LOCATION = "device.location"
    SCREEN_CAPTURE = "device.screen"

    # System actions
    NOTIFICATIONS = "notifications.send"
    SYSTEM_EXEC = "system.exec"
    SYSTEM_SMS = "system.sms"      # Android only, gated
    SYSTEM_INFO = "system.info"


# Default capability sets by node type
DEFAULT_CAPABILITIES: Dict[NodeType, List[NodeCapability]] = {
    NodeType.HEADLESS: [
        NodeCapability.CODE_READ,
        NodeCapability.CODE_WRITE,
        NodeCapability.CODE_EXEC,
        NodeCapability.CODE_TEST,
        NodeCapability.CODE_PR,
        NodeCapability.CODE_ENV,
        NodeCapability.SYSTEM_EXEC,
        NodeCapability.SYSTEM_INFO,
    ],
    NodeType.VSCODE: [
        NodeCapability.CODE_READ,
        NodeCapability.CODE_WRITE,
        NodeCapability.CODE_EXEC,
        NodeCapability.CODE_TEST,
        NodeCapability.CODE_PR,
        NodeCapability.CODE_ENV,
    ],
    NodeType.CANVAS: [
        NodeCapability.CANVAS_PRESENT,
        NodeCapability.CANVAS_NAVIGATE,
        NodeCapability.CANVAS_EVAL,
        NodeCapability.CANVAS_SNAPSHOT,
        NodeCapability.CANVAS_A2UI,
        NodeCapability.CANVAS_DASHBOARD,
        NodeCapability.SCREEN_CAPTURE,
    ],
    NodeType.MEDIA: [
        NodeCapability.MEDIA_RENDER,
        NodeCapability.MEDIA_VIZ,
        NodeCapability.MEDIA_VIDEO,
    ],
    NodeType.MOBILE_IOS: [
        NodeCapability.CAMERA_LIST,
        NodeCapability.CAMERA_SNAP,
        NodeCapability.CAMERA_CLIP,
        NodeCapability.LOCATION,
        NodeCapability.NOTIFICATIONS,
        NodeCapability.CANVAS_PRESENT,
        NodeCapability.CANVAS_SNAPSHOT,
        NodeCapability.SYSTEM_INFO,
    ],
    NodeType.MOBILE_ANDROID: [
        NodeCapability.CAMERA_LIST,
        NodeCapability.CAMERA_SNAP,
        NodeCapability.CAMERA_CLIP,
        NodeCapability.LOCATION,
        NodeCapability.NOTIFICATIONS,
        NodeCapability.SYSTEM_SMS,
        NodeCapability.SYSTEM_EXEC,
        NodeCapability.CANVAS_PRESENT,
        NodeCapability.SYSTEM_INFO,
    ],
    NodeType.CUSTOM: [],
}


@dataclass
class Node:
    """Registered companion node."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str = "unnamed-node"
    node_type: NodeType = NodeType.HEADLESS
    status: NodeStatus = NodeStatus.PENDING
    capabilities: List[NodeCapability] = field(default_factory=list)
    host: Optional[str] = None
    platform: Optional[str] = None  # e.g. "linux", "darwin", "android"
    metadata: Dict[str, Any] = field(default_factory=dict)
    paired_at: Optional[float] = None
    last_seen: Optional[float] = None
    allowlist: List[str] = field(default_factory=list)  # allowed command prefixes

    def __post_init__(self):
        if not self.capabilities:
            self.capabilities = list(DEFAULT_CAPABILITIES.get(self.node_type, []))
        if isinstance(self.node_type, str):
            self.node_type = NodeType(self.node_type)
        if isinstance(self.status, str):
            self.status = NodeStatus(self.status)
        # Normalize capability enums if they arrived as strings
        self.capabilities = [
            NodeCapability(c) if isinstance(c, str) else c for c in self.capabilities
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "host": self.host,
            "platform": self.platform,
            "metadata": self.metadata,
            "paired_at": self.paired_at,
            "last_seen": self.last_seen,
            "allowlist": self.allowlist,
        }

    def has_capability(self, command: str) -> bool:
        """Check whether this node can handle a command family (e.g. 'camera.snap')."""
        try:
            cap = NodeCapability(command)
            return cap in self.capabilities
        except ValueError:
            # Prefix match: "camera.snap" -> any camera.* capability
            family = command.split(".")[0]
            return any(c.value.startswith(family + ".") or c.value == command for c in self.capabilities)

    def touch(self) -> None:
        self.last_seen = time.time()

    def approve(self) -> None:
        self.status = NodeStatus.ONLINE
        self.paired_at = time.time()
        self.touch()

    def reject(self) -> None:
        self.status = NodeStatus.REJECTED
