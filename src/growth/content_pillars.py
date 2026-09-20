# Copyright © 2026 Chelsea Megan Woods
"""Content pillars — empowerment + real/raw life. Rage, jealousy, toxic energy allowed;
prefer turning intensity into agency and positive outcomes."""

from __future__ import annotations

from typing import TypedDict


class Pillar(TypedDict):
    id: str
    title: str
    intent: str
    example_angles: list[str]


CONTENT_PILLARS: list[Pillar] = [
    {
        "id": "healthy_boundaries",
        "title": "Setting healthy boundaries",
        "intent": "Limits that protect energy — can start from anger or exhaustion",
        "example_angles": [
            "The no that felt cruel and was actually self-respect",
            "Scripts for family guilt",
            "When flexibility was self-abandonment",
        ],
    },
    {
        "id": "toxic_dynamics",
        "title": "Toxic relationship dynamics",
        "intent": "Name patterns plainly; rage at the pattern is allowed",
        "example_angles": [
            "Intermittent reinforcement felt like chemistry",
            "Circular fights designed to exhaust you",
            "Small exits before the big one",
        ],
    },
    {
        "id": "confidence_resilience",
        "title": "Self-confidence and resilience",
        "intent": "Rebuild after being broken down",
        "example_angles": [
            "Evidence you survived what should have ended you",
            "Confidence after humiliation",
            "Resilience is not pretending it didn't hurt",
        ],
    },
    {
        "id": "positive_energy",
        "title": "Cultivating positive energy",
        "intent": "Peace after the storm — not fake positivity",
        "example_angles": [
            "Protecting your morning after a toxic night",
            "Cutting drains without a speech",
            "Joy as rebellion",
        ],
    },
    {
        "id": "jealousy_raw",
        "title": "Jealousy — raw and constructive",
        "intent": "Admit jealousy; use it as signal; optional turn to self-worth",
        "example_angles": [
            "The jealous thought you were ashamed to admit",
            "Comparison spiral → values checklist",
            "Wanting what she has without hating her",
        ],
    },
    {
        "id": "toxic_family",
        "title": "Toxic family and boundaries",
        "intent": "Family systems truth — anger welcome, agency preferred ending",
        "example_angles": [
            "Holiday rage and the boundary you finally kept",
            "Low contact is not betrayal",
            "Loving them and limiting access",
        ],
    },
    {
        "id": "female_rage",
        "title": "Female rage and real talk",
        "intent": "Valid anger at injustice, double standards, and emotional labor",
        "example_angles": [
            "I'm not 'too emotional' — I'm done absorbing it",
            "Rage as a boundary alarm",
            "From explosion to standard",
        ],
    },
]

# Owner policy: these are ALLOWED creative modes (not banned)
ALLOWED_INTENSITY = [
    "raw",
    "rage",
    "jealousy",
    "toxic_energy_themes",
    "confrontation",
    "engagement_hooks_from_real_pain",
]

STILL_OUT_OF_SCOPE = [
    "purchased_followers",
    "bot_farms",
    "coordinated_fake_engagement_pods",
    "content_promoting_self_harm_or_violence",
]


def growth_principles() -> dict:
    return {
        "follower_growth": (
            "Organic growth preferred: strong hooks, consistency, SEO/ASO. "
            "Raw/rage/jealousy content allowed. No bot/purchased follower services."
        ),
        "content_intensity": ALLOWED_INTENSITY,
        "creative_arc": "Often: truth in the dark → turn toward boundary, clarity, or power",
        "stack": {
            "content": "OpenAI / ChatGPT",
            "schedule": ["Publer", "FeedHive"],
            "policy": "Instinct + Apex ALLOW",
        },
        "out_of_scope": STILL_OUT_OF_SCOPE,
        "pillars": [p["id"] for p in CONTENT_PILLARS],
    }
