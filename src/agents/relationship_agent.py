# Relationship Continuity Agent (with Biometric Integration)
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any
from src.agents.biometric_stress import BiometricStressDetector

class RelationshipAgent:
    def __init__(self, router):
        self.router = router
        self.stress_detector = BiometricStressDetector()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        people = payload.get("people", [])
        context = payload.get("context", "")
        biometrics = payload.get("biometrics", {})
        
        stress_level = self.stress_detector.estimate_stress(biometrics)
        tone_instruction = self.stress_detector.adapt_agent_tone(stress_level)
        
        prompt = f"""You are Saphira's Relationship Continuity Agent.
Tone guidance: {tone_instruction}
People: {people}
Context: {context}
Detected stress level: {stress_level}

Suggest:
- Timely check-in messages (keep short and warm when stress is high)
- Gift or gesture ideas based on past context
- Simple coordination for gatherings

When the user is under high stress, prioritize low-effort actions that still maintain connection."""
        
        result = await self.router.generate_response(prompt)
        return {
            "status": "success",
            "agent": "relationship",
            "stress_level": stress_level,
            "suggestions": result,
            "category": "relationships"
        }
