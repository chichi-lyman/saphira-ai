# Improved Multi-Signal Biometric Stress Detection
# Copyright © 2026 Chelsea Megan Woods
#
# Combines HRV (primary), resting heart rate, and sleep score with
# mild non-linearity and explicit tone adaptation guidance for agents.

from typing import Dict, Any
import logging
import math

logger = logging.getLogger("SaphiraBiometric")


class BiometricStressDetector:
    """
    Multi-signal stress estimator.

    - Higher HRV → lower stress (typical healthy range ~40–100 ms)
    - Higher resting HR → higher stress
    - Lower sleep score → higher stress

    Returns both a discrete level (low / medium / high) and a full analysis
    dict so orchestrators can surface the raw score and tone guidance.
    """

    def __init__(self):
        # Soft thresholds on the final tanh-scaled score [0, 1]
        self.thresholds = {
            "low": 0.28,
            "medium": 0.55,
            "high": 0.78,
        }

    def _normalize_hrv(self, hrv: float) -> float:
        """Map 20–100 ms → 1.0 (high stress) → 0.0 (low stress)."""
        clamped = max(20.0, min(100.0, float(hrv)))
        return 1.0 - ((clamped - 20.0) / 80.0)

    def _normalize_resting_hr(self, hr: float) -> float:
        """Map 50–110 bpm → 0.0 → 1.0."""
        clamped = max(50.0, min(110.0, float(hr)))
        return (clamped - 50.0) / 60.0

    def _normalize_sleep(self, score: float) -> float:
        """Map 0–100 → 1.0 (poor) → 0.0 (excellent)."""
        clamped = max(0.0, min(100.0, float(score)))
        return 1.0 - (clamped / 100.0)

    def analyze(self, biometrics: Dict[str, Any]) -> Dict[str, Any]:
        """Full analysis used by LiveAgentOrchestrator and swarm."""
        hrv = float(biometrics.get("hrv", 55))
        resting_hr = float(biometrics.get("resting_hr", 70))
        sleep_score = float(biometrics.get("sleep_score", 70))

        hrv_c = self._normalize_hrv(hrv)
        hr_c = self._normalize_resting_hr(resting_hr)
        sleep_c = self._normalize_sleep(sleep_score)

        # Weighted combination (HRV dominant)
        raw = hrv_c * 0.45 + hr_c * 0.30 + sleep_c * 0.25

        # Soft non-linearity to compress extremes
        score = float(math.tanh(raw * 1.25))

        if score < self.thresholds["low"]:
            level = "low"
        elif score < self.thresholds["medium"]:
            level = "medium"
        else:
            level = "high"

        tone = self.adapt_agent_tone(level)

        analysis = {
            "stress_level": level,
            "stress_score": round(score, 4),
            "components": {
                "hrv_contribution": round(hrv_c, 4),
                "hr_contribution": round(hr_c, 4),
                "sleep_contribution": round(sleep_c, 4),
            },
            "inputs": {
                "hrv": hrv,
                "resting_hr": resting_hr,
                "sleep_score": sleep_score,
            },
            "tone_guidance": tone,
            "source": biometrics.get("source", "unknown"),
        }
        logger.debug("Stress analysis: %s", analysis)
        return analysis

    def estimate_stress(self, biometrics: Dict[str, float]) -> str:
        """Backward-compatible discrete level."""
        return self.analyze(biometrics)["stress_level"]

    def adapt_agent_tone(self, stress_level: str) -> str:
        if stress_level == "high":
            return (
                "Speak gently, keep answers short, prioritize recovery "
                "and one clear next step. Validate feelings first."
            )
        elif stress_level == "medium":
            return (
                "Be supportive and clear. Offer one small actionable step "
                "and keep the overall tone warm."
            )
        else:
            return "Normal confident and proactive tone."


# Alias kept for any external references that used the estimator name
BiometricStressEstimator = BiometricStressDetector
