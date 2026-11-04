from src.core.saphira_capability_catalog import AutonomyLevel, CapabilityCatalog
from src.core.saphira_agent_blueprint import CORE_AGENT_BLUEPRINTS
from src.orchestration.planner import TaskPlanner
from src.orchestration.registry import AgentRegistry


def test_catalog_contains_required_domains():
    catalog = CapabilityCatalog.default()
    # Keys defined in src/core/capabilities.json (current catalog)
    required = {
        "reasoning.plan",
        "memory.read",
        "memory.write",
        "quality.verify",
        "think.mode",
        "persona.conversation",
    }
    assert required.issubset(catalog.capabilities), (
        f"Missing: {required - set(catalog.capabilities)}"
    )
    # Commit-level capabilities require approval
    if catalog.get("commerce.purchase"):
        assert catalog.requires_commit_approval("commerce.purchase")
    mem = catalog.get("memory.read")
    assert mem is not None
    assert mem.minimum_autonomy in (AutonomyLevel.OBSERVE, AutonomyLevel.ASSIST)


def test_workforce_blueprint_is_complete():
    names = {agent.key for agent in CORE_AGENT_BLUEPRINTS}
    assert {
        "orchestrator",
        "samantha_persona",
        "stem_math",
        "cad_3d",
        "developer",
        "vision",
        "voice_audio",
        "os_hardware",
        "iot",
        "web_grounding",
        "memory",
        "proactive_planner",
        "communications",
        "commerce",
        "qa",
    }.issubset(names)


def test_planner_routes_new_domains_to_hidden_workers():
    task = TaskPlanner().create_task(
        "Use voice, inspect this screenshot, research the web, calculate the math, and remember the result"
    )
    agents = AgentRegistry().route(task)
    assert "voice_agent" in agents
    assert "vision_agent" in agents
    assert "research_agent" in agents
    assert "stem_agent" in agents
    assert "memory_agent" in agents
    assert "qa_agent" in agents
