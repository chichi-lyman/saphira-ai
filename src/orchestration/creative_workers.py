"""Creative co-creation workers for the six surreal systems.

Copyright © 2026 Chelsea Megan Woods
"""

from __future__ import annotations

import logging
from typing import Any

from .task import Task
from .workers import BaseSkillWorker

logger = logging.getLogger("SaphiraCreativeWorkers")


class BiometricAudioWorker(BaseSkillWorker):
    name = "biometric_audio_agent"
    capabilities = {"creative.biometric_audio", "voice", "iot"}
    skill = "saphira-creative-cocreator"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        logger.info("BiometricAudio on: %s", task.objective[:80])
        return self._envelope(
            task,
            step,
            {
                "system": "biometric_audio_ecosystem",
                "inputs": ["hrv", "brainwave_micro", "skin_temperature"],
                "output": "evolving ambient / electronic soundscape",
                "consent_required": True,
                "plan": f"Compose adaptive audio for: {task.objective}",
            },
        )


class EnvScriptingWorker(BaseSkillWorker):
    name = "env_scripting_agent"
    capabilities = {"creative.env_scripting", "content", "research"}
    skill = "saphira-creative-cocreator"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {
                "system": "contextual_environmental_scripting",
                "rewrites": ["narrative_events", "weather", "audio_freq", "npc_dialogue"],
                "plan": f"Adaptive world-state scripting for: {task.objective}",
            },
        )


class AbstractAvatarWorker(BaseSkillWorker):
    name = "abstract_avatar_agent"
    capabilities = {"creative.abstract_avatars", "vision", "content"}
    skill = "saphira-creative-cocreator"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {
                "system": "cyberpunk_abstract_avatars",
                "style": "procedural cyberpunk geometry / neon mystical",
                "morph": True,
                "photoreal_human": False,
                "plan": f"Living visual sculpture for: {task.objective}",
            },
        )


class EmotionalPaletteWorker(BaseSkillWorker):
    name = "emotional_palette_agent"
    capabilities = {"creative.emotional_palette", "content", "stem"}
    skill = "saphira-creative-cocreator"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {
                "system": "emotional_dataset_palette",
                "map": "text/poem sentiment → MIDI | lighting | brushstrokes",
                "plan": f"Cross-sensory translation for: {task.objective}",
            },
        )


class HoloArchitectureWorker(BaseSkillWorker):
    name = "holo_architecture_agent"
    capabilities = {"creative.holo_architecture", "iot", "vision"}
    skill = "saphira-creative-cocreator"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {
                "system": "responsive_holographic_architecture",
                "reactions": ["proximity_ripple", "mood_pocket_techno", "mood_pocket_minimal"],
                "plan": f"Room-scale holographic response for: {task.objective}",
            },
        )


class PromptWeavingWorker(BaseSkillWorker):
    name = "prompt_weaving_agent"
    capabilities = {"creative.prompt_weaving", "cad", "development"}
    skill = "saphira-creative-cocreator"

    async def execute(self, task: Task, step: dict[str, Any]) -> dict[str, Any] | None:
        return self._envelope(
            task,
            step,
            {
                "system": "algorithmic_prompt_weaving",
                "targets": ["loom", "3d_printer"],
                "variables": ["texture", "structural_density", "material_pattern"],
                "plan": f"Prompt→physical fabrication for: {task.objective}",
                "approval_likely": True,
            },
        )


def creative_workers() -> dict[str, Any]:
    workers = [
        BiometricAudioWorker(),
        EnvScriptingWorker(),
        AbstractAvatarWorker(),
        EmotionalPaletteWorker(),
        HoloArchitectureWorker(),
        PromptWeavingWorker(),
    ]
    return {w.name: w for w in workers}
