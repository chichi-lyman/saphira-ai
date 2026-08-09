"""Canonical capability catalog for Saphira's background workforce.

The catalog is declarative: it describes what an agent may do without forcing
provider-specific implementations into the executive runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class AutonomyLevel(IntEnum):
    OBSERVE = 0
    ASSIST = 1
    EXECUTE = 2
    COMMIT = 3


@dataclass(frozen=True)
class Capability:
    key: str
    description: str
    agent: str
    minimum_autonomy: AutonomyLevel = AutonomyLevel.ASSIST
    reversible: bool = True
    external_side_effect: bool = False
    tags: tuple[str, ...] = ()


@dataclass
class CapabilityCatalog:
    capabilities: dict[str, Capability] = field(default_factory=dict)

    @classmethod
    def default(cls) -> "CapabilityCatalog":
        items = [
            Capability("reasoning.plan", "decompose goals and coordinate workers", "orchestrator", AutonomyLevel.ASSIST, True, False, ("planning",)),
            Capability("persona.conversation", "generate adaptive conversational responses", "samantha_persona", AutonomyLevel.ASSIST, True, False, ("conversation",)),
            Capability("stem.calculate", "perform deterministic technical calculations", "stem_math", AutonomyLevel.ASSIST, True, False, ("math", "engineering")),
            Capability("cad.generate", "generate parametric CAD model instructions", "cad_3d", AutonomyLevel.ASSIST, True, False, ("cad", "3d")),
            Capability("code.sandbox", "write and execute code in an isolated sandbox", "developer", AutonomyLevel.EXECUTE, True, False, ("code", "debug")),
            Capability("vision.analyze", "analyze images, screenshots, OCR and visual context", "vision", AutonomyLevel.ASSIST, True, False, ("vision", "ocr")),
            Capability("voice.transcribe", "convert speech to text", "voice_audio", AutonomyLevel.ASSIST, True, False, ("voice", "stt")),
            Capability("voice.synthesize", "stream natural speech output", "voice_audio", AutonomyLevel.ASSIST, True, False, ("voice", "tts")),
            Capability("filesystem.read", "inspect permitted local files", "os_hardware", AutonomyLevel.OBSERVE, True, False, ("os", "files")),
            Capability("filesystem.write", "write permitted local files", "os_hardware", AutonomyLevel.EXECUTE, True, False, ("os", "files")),
            Capability("device.telemetry", "read permitted device telemetry", "os_hardware", AutonomyLevel.OBSERVE, True, False, ("hardware", "telemetry")),
            Capability("iot.read", "inspect permitted smart-environment state", "iot", AutonomyLevel.OBSERVE, True, False, ("iot", "home")),
            Capability("iot.control", "control permitted smart-environment devices", "iot", AutonomyLevel.COMMIT, True, True, ("iot", "home")),
            Capability("web.search", "retrieve current web information", "web_grounding", AutonomyLevel.ASSIST, True, False, ("web", "research")),
            Capability("memory.read", "retrieve relevant long-term context", "memory", AutonomyLevel.OBSERVE, True, False, ("memory",)),
            Capability("memory.write", "persist approved durable context", "memory", AutonomyLevel.EXECUTE, True, False, ("memory",)),
            Capability("schedule.create", "create scheduled/proactive workflows", "proactive_planner", AutonomyLevel.COMMIT, True, True, ("automation", "schedule")),
            Capability("communications.draft", "prepare external communications", "communications", AutonomyLevel.ASSIST, True, False, ("email", "messaging")),
            Capability("communications.send", "send external communications", "communications", AutonomyLevel.COMMIT, False, True, ("email", "messaging")),
            Capability("commerce.catalog", "inspect/manage permitted commerce catalog data", "commerce", AutonomyLevel.EXECUTE, True, True, ("commerce",)),
            Capability("commerce.purchase", "perform purchases or financial commerce actions", "commerce", AutonomyLevel.COMMIT, False, True, ("commerce", "finance")),
            Capability("quality.verify", "validate task outputs against acceptance criteria", "qa", AutonomyLevel.OBSERVE, True, False, ("qa", "verification")),
        ]
        return cls({item.key: item for item in items})

    def get(self, key: str) -> Capability | None:
        return self.capabilities.get(key)

    def for_agent(self, agent: str) -> list[Capability]:
        return [c for c in self.capabilities.values() if c.agent == agent]

    def requires_commit_approval(self, key: str) -> bool:
        capability = self.get(key)
        return bool(capability and capability.minimum_autonomy >= AutonomyLevel.COMMIT)
