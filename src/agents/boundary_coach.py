# Boundary & Difficult Conversation Coach (with Biometric Integration)
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any
from src.agents.biometric_stress import BiometricStressDetector

class BoundaryCoachAgent:
    def __init__(self, router):
        self.router = router
        self.stress_detector = BiometricStressDetector()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        situation = payload.get("situation", "")
        emotion = payload.get("emotion", "anxious")
        biometrics = payload.get("biometrics", {})
        
        stress_level = self.stress_detector.estimate_stress(biometrics)
        tone_instruction = self.stress_detector.adapt_agent_tone(stress_level)
        
        prompt = f"""You are Saphira's Boundary Coach.
Tone guidance: {tone_instruction}
User situation: {situation}
Current emotion: {emotion}
Detected stress level: {stress_level}

Draft 2-3 clear, firm but kind message options.
Simulate likely responses and suggest next steps.
When stress is high, keep language especially gentle and short.
Keep overall style warm, grounded, and free of fluff."""
        
        result = await self.router.generate_response(prompt)
        return {
            "status": "success",
            "agent": "boundary_coach",
            "stress_level": stress_level,
            "suggestions": result,
            "category": "emotional"
        }
