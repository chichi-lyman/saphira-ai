# Expanded Intent Classifier (beyond simple keyword matching)
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any, List, Tuple
import re


class IntentClassifier:
    """
    Lightweight hybrid classifier that combines:
    1. Keyword / phrase matching
    2. Simple semantic scoring (token overlap + weighting)
    3. Confidence thresholds with fallback
    """

    def __init__(self):
        # Weighted intent patterns (higher weight = stronger signal)
        self.intent_patterns: Dict[str, List[Tuple[str, float]]] = {
            "boundary_coach": [
                (r"\b(boundary|boundaries)\b", 1.5),
                (r"\b(difficult conversation|hard talk|confrontation)\b", 1.4),
                (r"\b(set a limit|stand up for myself|toxic)\b", 1.3),
                (r"\b(argue|conflict|fight with)\b", 1.0),
            ],
            "admin_resolver": [
                (r"\b(medical bill|insurance claim|disputed bill)\b", 1.6),
                (r"\b(bureaucracy|appeal|tax|irs)\b", 1.4),
                (r"\b(customer service|phone tree|hold for hours)\b", 1.3),
                (r"\b(bill|claim|refund|dispute)\b", 1.0),
            ],
            "relationship": [
                (r"\b(friend|family|relationship|partner)\b", 1.3),
                (r"\b(check[- ]?in|reach out|catch up)\b", 1.4),
                (r"\b(gift idea|birthday|anniversary)\b", 1.2),
                (r"\b(lonely|miss them|haven't talked)\b", 1.1),
            ],
            "lifestyle_orchestrator": [
                (r"\b(workout|exercise|gym|run)\b", 1.3),
                (r"\b(sleep|tired|insomnia|rest)\b", 1.4),
                (r"\b(meal|recipe|eat|dinner|lunch)\b", 1.2),
                (r"\b(habit|routine|stress|energy|burnout)\b", 1.3),
            ],
        }

    def classify(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        scores: Dict[str, float] = {intent: 0.0 for intent in self.intent_patterns}

        for intent, patterns in self.intent_patterns.items():
            for pattern, weight in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    scores[intent] += weight * len(matches)

        # Normalize and pick winner
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        # Confidence threshold
        if best_score < 0.8:
            return {
                "intent": "general",
                "confidence": best_score,
                "scores": scores,
                "fallback": True
            }

        return {
            "intent": best_intent,
            "confidence": best_score,
            "scores": scores,
            "fallback": False
        }

    def route(self, text: str) -> str:
        """Convenience method that returns only the agent name."""
        result = self.classify(text)
        mapping = {
            "boundary_coach": "boundary_coach",
            "admin_resolver": "admin_resolver",
            "relationship": "relationship",
            "lifestyle_orchestrator": "lifestyle_orchestrator",
            "general": "boundary_coach",  # safe default
        }
        return mapping.get(result["intent"], "boundary_coach")
