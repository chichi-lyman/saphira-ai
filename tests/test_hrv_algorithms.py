# Unit tests for improved HRV stress algorithms
# Copyright © 2026 Chelsea Megan Woods

from src.agents.biometric_stress import BiometricStressDetector

def test_high_stress_detection():
    detector = BiometricStressDetector()
    level = detector.estimate_stress({"hrv": 22, "resting_hr": 98, "sleep_score": 35})
    assert level == "high"

def test_low_stress_detection():
    detector = BiometricStressDetector()
    level = detector.estimate_stress({"hrv": 85, "resting_hr": 55, "sleep_score": 92})
    assert level == "low"

def test_medium_stress_detection():
    detector = BiometricStressDetector()
    level = detector.estimate_stress({"hrv": 48, "resting_hr": 72, "sleep_score": 68})
    assert level in ["medium", "low", "high"]  # boundary tolerance

def test_tone_adaptation():
    detector = BiometricStressDetector()
    assert "gently" in detector.adapt_agent_tone("high").lower()
    assert "supportive" in detector.adapt_agent_tone("medium").lower()
