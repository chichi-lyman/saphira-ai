import json
from types import SimpleNamespace

import pytest

from src.core.awareness_loop import SaphiraAwarenessEngine


class FakeModels:
    async def generate_content(self, **kwargs):
        return SimpleNamespace(text=json.dumps({
            "status": "COMPLETED",
            "next_action": "none",
            "issue_detected": "none",
        }))


class FakeAio:
    def __init__(self):
        self.models = FakeModels()


class FakeClient:
    def __init__(self):
        self.aio = FakeAio()


@pytest.mark.asyncio
async def test_awareness_loop_completes_without_executing_shell(monkeypatch):
    engine = SaphiraAwarenessEngine.__new__(SaphiraAwarenessEngine)
    engine.client = FakeClient()
    engine.sensors = SimpleNamespace(
        capture_vision_frame=lambda: "",
        image_part=lambda _: None,
    )

    result = await engine.execute_goal_with_awareness("verify dashboard")

    assert result["status"] == "SUCCESS"
    assert result["history"][0]["evaluation"]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_awareness_loop_never_executes_model_action(monkeypatch):
    engine = SaphiraAwarenessEngine.__new__(SaphiraAwarenessEngine)
    engine.client = FakeClient()
    engine.sensors = SimpleNamespace(
        capture_vision_frame=lambda: "",
        image_part=lambda _: None,
    )

    called = False

    async def forbidden(*args, **kwargs):
        nonlocal called
        called = True

    engine._run_system_command = forbidden
    result = await engine.execute_goal_with_awareness("inspect environment")

    assert result["status"] == "SUCCESS"
    assert called is False
