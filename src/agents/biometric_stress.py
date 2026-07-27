# Improved HRV Stress Detection Algorithms
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any
import logging
import math

logger = logging.getLogger("SaphiraBiometric")

class BiometricStressDetector:
    """
    Multi-signal stress estimator using HRV, resting HR, and sleep quality.
    Implements a more robust algorithm than the original linear version.
    """

    def __init__(self):
        self.thresholds = {
            "low": 0.28,
            "medium": 0.55,
            "high": 0.78
        }

    def _normalize_hrv(self, hrv: float) -> float:
        """Higher HRV = lower stress. Typical healthy range ~40-100 ms."""
        # Map 20–100 ms → 1.0 → 0.0 stress contribution
        clamped = max(20.0, min(100.0, hrv))
        return 1.0 - ((clamped - 20.0) / 80.0)

    def _normalize_resting_hr(self, hr: float) -> float:
        """Higher resting HR = higher stress."""
        clamped = max(50.0, min(110.0, hr))
        return (clamped - 50.0) / 60.0

    def _normalize_sleep(self, score: float) -> float:
        """Lower sleep score = higher stress."""
        clamped = max(0.0, min(100.0, score))
        return 1.0 - (clamped / 100.0)

    def estimate_stress(self, biometrics: Dict[str, float]) -> str:
        hrv = float(biometrics.get("hrv", 55))
        resting_hr = float(biometrics.get("resting_hr", 70))
        sleep_score = float(biometrics.get("sleep_score", 70))

        # Weighted combination with mild non-linearity
        raw = (
            self._normalize_hrv(hrv) * 0.45 +
            self._normalize_resting_hr(resting_hr) * 0.30 +
            self._normalize_sleep(sleep_score) * 0.25
        )

        # Soften extremes
        score = math.tanh(raw * 1.2)

        if score < self.thresholds["low"]:
            level = "low"
        elif score < self.thresholds["medium"]:
            level = "medium"
        else:
            level = "high"

        logger.debug(f"Stress score={score:.3f} → {level}")
        return level

    def adapt_agent_tone(self, stress_level: str) -> str:
        if stress_level == "high":
            return "Speak gently, keep answers short, prioritize recovery and one clear next step."
        elif stress_level == "medium":
            return "Be supportive and clear. Offer one small actionable step."
        else:
            return "Normal confident and proactive tone."
