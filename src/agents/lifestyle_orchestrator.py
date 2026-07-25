# Adaptive Lifestyle Orchestrator (with Biometric Integration)
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any
from src.agents.biometric_stress import BiometricStressDetector

class LifestyleOrchestratorAgent:
    def __init__(self, router):
        self.router = router
        self.stress_detector = BiometricStressDetector()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        calendar = payload.get("calendar", [])
        biometrics = payload.get("biometrics", {})
        
        # Estimate stress and adapt tone
        stress_level = self.stress_detector.estimate_stress(biometrics)
        tone_instruction = self.stress_detector.adapt_agent_tone(stress_level)
        
        prompt = f"""You are Saphira's Adaptive Lifestyle Orchestrator.
Tone guidance: {tone_instruction}
Calendar: {calendar}
Stress Level: {stress_level}
Biometrics: {biometrics}

Generate a realistic daily adjustment plan:
- Scaled workout or recovery based on stress
- Meal suggestion based on available time/energy
- Sleep window recommendation
Make it 1% better and sustainable. Keep responses concise when stress is high."""
        
        result = await self.router.generate_response(prompt)
        return {
            "status": "success",
            "agent": "lifestyle_orchestrator",
            "stress_level": stress_level,
            "plan": result,
            "category": "wellness"
        }
