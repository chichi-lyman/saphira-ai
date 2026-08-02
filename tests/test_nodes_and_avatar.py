# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.

import pytest
from src.nodes.registry import NodeRegistry
from src.nodes.base import NodeType, NodeStatus
from src.avatar.grok_avatar_service import GrokAvatarService, AvatarState, CHELSEA_VISUAL_DNA


def test_node_register_and_approve():
    reg = NodeRegistry()
    node = reg.register("test-phone", node_type="mobile_android", auto_approve=False)
    assert node.status == NodeStatus.PENDING
    reg.approve(node.id)
    assert reg.get(node.id).status == NodeStatus.ONLINE
    assert any(c.value.startswith("camera.") for c in node.capabilities)


def test_node_capability_search():
    reg = NodeRegistry()
    reg.register("dev", node_type="headless", auto_approve=True)
    reg.register("ui", node_type="canvas", auto_approve=True)
    code_nodes = reg.find_by_capability("code.exec")
    assert len(code_nodes) >= 1
    canvas_nodes = reg.find_by_capability("canvas.dashboard")
    assert len(canvas_nodes) >= 1


@pytest.mark.asyncio
async def test_node_invoke_simulation():
    from src.nodes.invoke import NodeInvoker
    from src.nodes.registry import NodeRegistry

    reg = NodeRegistry()
    reg.register("saphira-canvas", node_type="canvas", auto_approve=True)
    inv = NodeInvoker(reg)
    result = await inv.invoke("saphira-canvas", "canvas.dashboard", {"title": "Test"})
    assert result.get("status") == "ok"
    assert result.get("action") == "canvas.dashboard"


def test_avatar_prompt_contains_chelsea_dna():
    svc = GrokAvatarService(api_key=None)
    prompt = svc.build_prompt(AvatarState.WELCOME)
    assert "Chelsea Megan Woods" in prompt
    assert "platinum" in prompt.lower() or "blonde" in prompt.lower()
    assert "electric blue" in prompt.lower() or "ultraviolet" in prompt.lower()
    assert CHELSEA_VISUAL_DNA.split(",")[0] in prompt


def test_avatar_stub_without_key():
    svc = GrokAvatarService(api_key=None)
    out = svc.generate_frame(state=AvatarState.TALKING)
    assert out["status"] == "stub"
    assert out["state"] == "talking"
    assert "prompt" in out
