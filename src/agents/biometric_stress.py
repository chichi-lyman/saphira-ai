# Biometric Stress Detection Integration
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any
import logging

logger = logging.getLogger("SaphiraBiometric")

class BiometricStressDetector:
    """
    Integrates with wearables (heart rate variability, skin conductance, sleep data)
    to estimate real-time stress and adapt agent behavior.
    """

    def __init__(self):
        self.thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.85
        }

    def estimate_stress(self, biometrics: Dict[str, float]) -> str:
        """
        Simple weighted model:
        - High HRV = lower stress
        - High resting HR or low sleep quality = higher stress
        """
        hrv = biometrics.get("hrv", 50)
        resting_hr = biometrics.get("resting_hr", 70)
        sleep_score = biometrics.get("sleep_score", 70)

        # Normalize (very rough heuristic)
        stress_score = (
            (100 - hrv) / 100 * 0.4 +
            (resting_hr - 50) / 50 * 0.3 +
            (100 - sleep_score) / 100 * 0.3
        )

        if stress_score < self.thresholds["low"]:
            return "low"
        elif stress_score < self.thresholds["medium"]:
            return "medium"
        else:
            return "high"

    def adapt_agent_tone(self, stress_level: str) -> str:
        if stress_level == "high":
            return "Speak gently, offer shorter responses, prioritize recovery."
        elif stress_level == "medium":
            return "Be supportive and clear. Offer one small next step."
        else:
            return "Normal confident and proactive tone."
