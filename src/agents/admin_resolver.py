# Admin & Bureaucracy Resolver Agent (with Biometric Integration)
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any
from src.agents.biometric_stress import BiometricStressDetector
from src.integrations.wearable_connector import wearable_connector


class AdminResolverAgent:
    def __init__(self, router):
        self.router = router
        self.stress_detector = BiometricStressDetector()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        issue = payload.get("issue", "")
        documents = payload.get("documents", [])
        biometrics = payload.get("biometrics") or wearable_connector.fetch_live_biometrics()

        stress_level = self.stress_detector.estimate_stress(biometrics)
        tone_instruction = self.stress_detector.adapt_agent_tone(stress_level)

        prompt = f"""You are Saphira's Admin Resolver.
Tone guidance: {tone_instruction}
Issue: {issue}
Available documents: {documents}
Detected stress level: {stress_level}

Create a clear step-by-step action plan:
1. What to say on the phone (keep short if stress is high)
2. Exact policy references if possible
3. Draft appeal letter (gentle and firm)
4. Follow-up checklist

When the user is under high stress, prioritize the absolute minimum steps needed and offer emotional validation first."""

        result = await self.router.generate_response(prompt)
        return {
            "status": "success",
            "agent": "admin_resolver",
            "stress_level": stress_level,
            "plan": result,
            "category": "administrative",
            "biometrics_source": biometrics.get("source"),
        }
