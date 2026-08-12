"""Platform-facing biometric stress detection (multi-signal)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
import math

@dataclass
class StressAnalysis:
    stress_level: str
    stress_score: float
    components: Dict[str, float]
    tone_guidance: str
    raw: Dict[str, Any]

class BiometricStressService:
    def __init__(self) -> None:
        self.thresholds = {"low": 0.28, "medium": 0.55, "high": 0.78}

    def _norm_hrv(self, hrv: float) -> float:
        clamped = max(20.0, min(100.0, float(hrv)))
        return 1.0 - ((clamped - 20.0) / 80.0)

    def _norm_hr(self, hr: float) -> float:
        clamped = max(50.0, min(110.0, float(hr)))
        return (clamped - 50.0) / 60.0

    def _norm_sleep(self, score: float) -> float:
        clamped = max(0.0, min(100.0, float(score)))
        return 1.0 - (clamped / 100.0)

    def analyze(self, biometrics: Dict[str, Any]) -> StressAnalysis:
        hrv = float(biometrics.get("hrv", 55))
        resting_hr = float(biometrics.get("resting_hr", 70))
        sleep_score = float(biometrics.get("sleep_score", 70))
        hrv_c = self._norm_hrv(hrv)
        hr_c = self._norm_hr(resting_hr)
        sleep_c = self._norm_sleep(sleep_score)
        raw = hrv_c * 0.45 + hr_c * 0.30 + sleep_c * 0.25
        score = float(math.tanh(raw * 1.25))
        if score < self.thresholds["low"]:
            level = "low"
        elif score < self.thresholds["medium"]:
            level = "medium"
        else:
            level = "high"
        tone = {"low": "energetic_supportive", "medium": "calm_supportive", "high": "gentle_minimal_load"}.get(level, "calm_supportive")
        return StressAnalysis(
            stress_level=level,
            stress_score=round(score, 4),
            components={"hrv_contribution": round(hrv_c, 4), "hr_contribution": round(hr_c, 4), "sleep_contribution": round(sleep_c, 4)},
            tone_guidance=tone,
            raw={"hrv": hrv, "resting_hr": resting_hr, "sleep_score": sleep_score},
        )

biometric_stress = BiometricStressService()
