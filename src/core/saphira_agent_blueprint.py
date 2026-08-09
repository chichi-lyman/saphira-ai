"""Canonical blueprint for Saphira's complete background workforce."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentBlueprint:
    key: str
    mission: str
    capabilities: tuple[str, ...]
    background: bool = True


CORE_AGENT_BLUEPRINTS: tuple[AgentBlueprint, ...] = (
    AgentBlueprint("orchestrator", "Plan, delegate, coordinate and resolve conflicts.", ("reasoning.plan",)),
    AgentBlueprint("samantha_persona", "Own the conversational relationship, tone and response presentation.", ("persona.conversation",)),
    AgentBlueprint("stem_math", "Solve deterministic mathematics, science and engineering tasks.", ("stem.calculate",)),
    AgentBlueprint("cad_3d", "Generate and validate parametric CAD/3D model specifications.", ("cad.generate",)),
    AgentBlueprint("developer", "Generate, test, debug, refactor and safely execute code.", ("code.sandbox",)),
    AgentBlueprint("vision", "Interpret images, screenshots, OCR and visual context.", ("vision.analyze",)),
    AgentBlueprint("voice_audio", "Run speech recognition, speech synthesis and interruption-aware audio flows.", ("voice.transcribe", "voice.synthesize")),
    AgentBlueprint("os_hardware", "Operate explicitly permitted local files, applications and telemetry.", ("filesystem.read", "filesystem.write", "device.telemetry")),
    AgentBlueprint("iot", "Operate permitted smart-home and physical-environment integrations.", ("iot.read", "iot.control")),
    AgentBlueprint("web_grounding", "Retrieve current external information and verify facts.", ("web.search",)),
    AgentBlueprint("memory", "Recall and persist long-term, episodic, semantic and procedural context.", ("memory.read", "memory.write")),
    AgentBlueprint("proactive_planner", "Monitor schedules/events and launch authorized proactive workflows.", ("schedule.create",)),
    AgentBlueprint("communications", "Prepare and, after approval, send external communications.", ("communications.draft", "communications.send")),
    AgentBlueprint("commerce", "Operate permitted commerce/catalog workflows and gate purchases.", ("commerce.catalog", "commerce.purchase")),
    AgentBlueprint("qa", "Verify outputs, acceptance criteria, artifacts and task completion.", ("quality.verify",)),
)


def get_agent_blueprint(key: str) -> AgentBlueprint | None:
    return next((agent for agent in CORE_AGENT_BLUEPRINTS if agent.key == key), None)
