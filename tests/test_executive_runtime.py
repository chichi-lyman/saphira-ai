import asyncio

from src.assistant.runtime import build_saphira
from src.orchestration.task import TaskStatus


class FakeResearchAgent:
    name = "research_agent"
    capabilities = {"research"}

    async def execute(self, task, step):
        return {"type": "research", "summary": "research completed"}


class FakeQAAgent:
    name = "qa_agent"
    capabilities = {"quality"}

    async def execute(self, task, step):
        return {"type": "qa", "passed": True}


def test_conversation_routes_to_hidden_workers():
    assistant = build_saphira([FakeResearchAgent(), FakeQAAgent()])
    task = assistant.accept("Research the best options and compare them")

    assert task.status == TaskStatus.PLANNED
    assert "research_agent" in task.assigned_agents
    assert "qa_agent" in task.assigned_agents
    assert "research_agent" not in task.objective


def test_autonomous_task_executes_and_is_remembered():
    assistant = build_saphira([FakeResearchAgent(), FakeQAAgent()])
    task = assistant.accept("Research the best options")

    result = asyncio.run(assistant.execute(task.id))

    assert result.status == TaskStatus.COMPLETED
    assert assistant.memory.recent_tasks(1)[0]["task_id"] == task.id


def test_external_action_waits_for_approval():
    assistant = build_saphira()
    task = assistant.accept("Send an email to the client")

    assert task.status == TaskStatus.WAITING_APPROVAL
    assert task.autonomy.requires_approval is True
    assert assistant.respond(task).startswith("I’ve prepared this")
