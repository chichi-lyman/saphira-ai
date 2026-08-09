from src.core.saphira_capability_catalog import AutonomyLevel, CapabilityCatalog
from src.core.saphira_agent_blueprint import CORE_AGENT_BLUEPRINTS
from src.orchestration.planner import TaskPlanner
from src.orchestration.registry import AgentRegistry


def test_catalog_contains_required_domains():
    catalog = CapabilityCatalog.default()
    required = {
        "reasoning.plan", "voice.transcribe", "voice.synthesize", "vision.analyze",
        "code.sandbox", "cad.generate", "stem.calculate", "filesystem.read",
        "iot.control", "web.search", "memory.read", "schedule.create",
        "communications.send", "commerce.purchase", "quality.verify",
    }
    assert required.issubset(catalog.capabilities)
    assert catalog.requires_commit_approval("commerce.purchase")
    assert catalog.get("web.search").minimum_autonomy == AutonomyLevel.ASSIST


def test_workforce_blueprint_is_complete():
    names = {agent.key for agent in CORE_AGENT_BLUEPRINTS}
    assert {
        "orchestrator", "samantha_persona", "stem_math", "cad_3d", "developer",
        "vision", "voice_audio", "os_hardware", "iot", "web_grounding", "memory",
        "proactive_planner", "communications", "commerce", "qa",
    }.issubset(names)


def test_planner_routes_new_domains_to_hidden_workers():
    task = TaskPlanner().create_task("Use voice, inspect this screenshot, research the web, calculate the math, and remember the result")
    agents = AgentRegistry().route(task)
    assert "voice_agent" in agents
    assert "vision_agent" in agents
    assert "research_agent" in agents
    assert "stem_agent" in agents
    assert "memory_agent" in agents
    assert "qa_agent" in agents
