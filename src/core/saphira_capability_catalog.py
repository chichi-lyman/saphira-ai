"""Canonical capability catalog for Saphira's background workforce.

The catalog is declarative: it describes what an agent may do without forcing
provider-specific implementations into the executive runtime.

Competitive parity targets (OpenAI, Anthropic, Google, Microsoft, Meta,
Perplexity, xAI, DeepSeek) are encoded as capability keys so the orchestrator
can route toward category leaders' strengths while the unified runtime aims
for a 1% product edge via verification, memory, and policy.
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
            # --- Core executive loop ---
            Capability("reasoning.plan", "decompose goals and coordinate workers", "orchestrator", AutonomyLevel.ASSIST, True, False, ("planning", "openai-parity")),
            Capability("persona.conversation", "generate adaptive conversational responses", "samantha_persona", AutonomyLevel.ASSIST, True, False, ("conversation", "openai-parity")),
            Capability("quality.verify", "validate task outputs against acceptance criteria", "qa", AutonomyLevel.OBSERVE, True, False, ("qa", "verification", "edge")),
            Capability("memory.read", "retrieve relevant long-term context", "memory", AutonomyLevel.OBSERVE, True, False, ("memory", "edge")),
            Capability("memory.write", "persist approved durable context", "memory", AutonomyLevel.EXECUTE, True, False, ("memory", "edge")),
            # --- STEM / xAI + DeepSeek parity ---
            Capability("stem.calculate", "perform deterministic technical calculations", "stem_math", AutonomyLevel.ASSIST, True, False, ("math", "engineering", "xai-parity", "deepseek-parity")),
            Capability("stem.reason", "direct math, physics, and logic reasoning with tool grounding", "stem_math", AutonomyLevel.ASSIST, True, False, ("math", "physics", "xai-parity", "deepseek-parity")),
            # --- Expanded CS / AI domain mastery (top-20 university structures) ---
            Capability("ai.machine_learning", "deep learning, reinforcement learning, probabilistic modeling, knowledge representation", "stem_math", AutonomyLevel.ASSIST, True, False, ("ai", "ml", "xai-parity", "deepseek-parity", "edge")),
            Capability("ai.nlp", "computational linguistics, speech recognition, large language models", "stem_math", AutonomyLevel.ASSIST, True, False, ("ai", "nlp", "openai-parity", "edge")),
            Capability("ai.computer_vision", "image processing, 3D graphics, generative visual models, AR/VR", "vision", AutonomyLevel.ASSIST, True, False, ("ai", "vision", "google-parity", "edge")),
            Capability("ai.robotics", "intelligent kinematics, mechatronics, motion planning, autonomous navigation", "stem_math", AutonomyLevel.ASSIST, True, False, ("ai", "robotics", "edge")),
            Capability("ai.human_ai_interaction", "user-centered AI design, trustworthy systems, ethics in automation", "samantha_persona", AutonomyLevel.ASSIST, True, False, ("ai", "hai", "ethics", "edge")),
            Capability("cs.curriculum", "map and reason over top-20 CS/AI degree structures, tracks, and joint majors", "web_grounding", AutonomyLevel.ASSIST, True, False, ("cs", "education", "edge")),
            Capability("cs.interdisciplinary", "computation & cognition, computational biology, applied math/stats, EECS integration", "stem_math", AutonomyLevel.ASSIST, True, False, ("cs", "interdisciplinary", "edge")),
            # --- AI careers and compensation (durable market knowledge) ---
            Capability("ai.careers", "advise on AI professional roles, responsibilities, career pathways, and U.S. compensation ranges", "web_grounding", AutonomyLevel.ASSIST, True, False, ("ai", "careers", "compensation", "edge")),
            Capability("ai.compensation", "benchmark base salary and total compensation packages for AI research, engineering, architecture, product, MLOps, and ethics roles", "web_grounding", AutonomyLevel.ASSIST, True, False, ("ai", "compensation", "careers", "edge")),
            # --- CAD ---
            Capability("cad.generate", "generate parametric CAD model instructions", "cad_3d", AutonomyLevel.ASSIST, True, False, ("cad", "3d")),
            # --- Anthropic parity: software engineering ---
            Capability("code.sandbox", "write and execute code in an isolated sandbox", "developer", AutonomyLevel.EXECUTE, True, False, ("code", "debug", "anthropic-parity")),
            Capability("code.refactor", "refactor and improve large codebases with tests", "developer", AutonomyLevel.EXECUTE, True, False, ("code", "refactor", "anthropic-parity")),
            Capability("code.review", "review diffs for correctness, security, and style", "developer", AutonomyLevel.ASSIST, True, False, ("code", "review", "anthropic-parity")),
            Capability("document.long_context", "analyze large documents, books, and legal packs in structured passes", "web_grounding", AutonomyLevel.ASSIST, True, False, ("documents", "anthropic-parity")),
            # --- OpenAI / Google multimodal parity ---
            Capability("vision.analyze", "analyze images, screenshots, OCR and visual context", "vision", AutonomyLevel.ASSIST, True, False, ("vision", "ocr", "openai-parity", "google-parity")),
            Capability("media.generate", "generate or orchestrate image/video media under policy", "vision", AutonomyLevel.EXECUTE, True, True, ("media", "google-parity")),
            Capability("voice.transcribe", "convert speech to text", "voice_audio", AutonomyLevel.ASSIST, True, False, ("voice", "stt", "openai-parity")),
            Capability("voice.synthesize", "stream natural speech output", "voice_audio", AutonomyLevel.ASSIST, True, False, ("voice", "tts", "openai-parity")),
            # --- OS / device ---
            Capability("filesystem.read", "inspect permitted local files", "os_hardware", AutonomyLevel.OBSERVE, True, False, ("os", "files")),
            Capability("filesystem.write", "write permitted local files", "os_hardware", AutonomyLevel.EXECUTE, True, False, ("os", "files")),
            Capability("device.telemetry", "read permitted device telemetry", "os_hardware", AutonomyLevel.OBSERVE, True, False, ("hardware", "telemetry")),
            # --- IoT ---
            Capability("iot.read", "inspect permitted smart-environment state", "iot", AutonomyLevel.OBSERVE, True, False, ("iot", "home")),
            Capability("iot.control", "control permitted smart-environment devices", "iot", AutonomyLevel.COMMIT, True, True, ("iot", "home")),
            # --- Perplexity parity: research & citations ---
            Capability("web.search", "retrieve current web information", "web_grounding", AutonomyLevel.ASSIST, True, False, ("web", "research", "perplexity-parity")),
            Capability("research.cite", "synthesize research with explicit citations and source artifacts", "web_grounding", AutonomyLevel.ASSIST, True, False, ("web", "citations", "perplexity-parity")),
            Capability("research.factcheck", "cross-check claims against live sources before final answer", "qa", AutonomyLevel.OBSERVE, True, False, ("qa", "factcheck", "perplexity-parity")),
            # --- Microsoft / Google productivity parity ---
            Capability("schedule.create", "create scheduled/proactive workflows", "proactive_planner", AutonomyLevel.COMMIT, True, True, ("automation", "schedule", "microsoft-parity")),
            Capability("workspace.assist", "draft and transform documents, sheets, and slides via connectors", "communications", AutonomyLevel.ASSIST, True, False, ("productivity", "microsoft-parity", "google-parity")),
            Capability("communications.draft", "prepare external communications", "communications", AutonomyLevel.ASSIST, True, False, ("email", "messaging", "microsoft-parity")),
            Capability("communications.send", "send external communications", "communications", AutonomyLevel.COMMIT, False, True, ("email", "messaging", "microsoft-parity")),
            # --- Meta parity: open customization & social ---
            Capability("model.route", "select cost/quality-appropriate provider model without user-visible churn", "orchestrator", AutonomyLevel.ASSIST, True, False, ("routing", "meta-parity", "deepseek-parity", "edge")),
            Capability("social.engage", "prepare or execute permitted social/platform actions", "communications", AutonomyLevel.COMMIT, False, True, ("social", "meta-parity", "xai-parity")),
            # --- Commerce ---
            Capability("commerce.catalog", "inspect/manage permitted commerce catalog data", "commerce", AutonomyLevel.EXECUTE, True, True, ("commerce",)),
            Capability("commerce.purchase", "perform purchases or financial commerce actions", "commerce", AutonomyLevel.COMMIT, False, True, ("commerce", "finance")),
            # --- Agentic workflows (OpenAI-class) ---
            Capability("agent.workflow", "run multi-step autonomous tool workflows under policy", "orchestrator", AutonomyLevel.EXECUTE, True, True, ("agentic", "openai-parity")),
            Capability("enterprise.secure", "apply enterprise RBAC, audit, and privacy constraints to actions", "orchestrator", AutonomyLevel.OBSERVE, True, False, ("security", "microsoft-parity", "edge")),
        ]
        return cls({item.key: item for item in items})

    def get(self, key: str) -> Capability | None:
        return self.capabilities.get(key)

    def for_agent(self, agent: str) -> list[Capability]:
        return [c for c in self.capabilities.values() if c.agent == agent]

    def by_tag(self, tag: str) -> list[Capability]:
        return [c for c in self.capabilities.values() if tag in c.tags]

    def competitive_parity_keys(self) -> dict[str, list[str]]:
        """Map competitor tag suffix -> capability keys for reporting."""
        tags = (
            "openai-parity",
            "anthropic-parity",
            "google-parity",
            "microsoft-parity",
            "meta-parity",
            "perplexity-parity",
            "xai-parity",
            "deepseek-parity",
            "edge",
        )
        return {t: [c.key for c in self.by_tag(t)] for t in tags}

    def requires_commit_approval(self, key: str) -> bool:
        capability = self.get(key)
        return bool(capability and capability.minimum_autonomy >= AutonomyLevel.COMMIT)
