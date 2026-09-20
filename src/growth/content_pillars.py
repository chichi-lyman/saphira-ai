# Copyright © 2026 Chelsea Megan Woods
"""Empowerment content pillars — no rage-bait / jealousy clickbait / toxic energy farming."""

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
        "intent": "Teach clear, kind limits that protect energy without cruelty",
        "example_angles": [
            "Scripts for saying no without over-explaining",
            "Boundaries with family vs partners vs work",
            "Repairing after you abandoned your own boundary",
        ],
    },
    {
        "id": "toxic_dynamics",
        "title": "Recognizing and navigating toxic relationship dynamics",
        "intent": "Name patterns so readers can choose safety and clarity",
        "example_angles": [
            "Intermittent reinforcement and why it feels like chemistry",
            "When empathy becomes self-erasure",
            "Leaving loops: small exits before big ones",
        ],
    },
    {
        "id": "confidence_resilience",
        "title": "Building self-confidence and resilience",
        "intent": "Practical self-trust, not toxic positivity",
        "example_angles": [
            "Evidence journal: proof you keep promises to yourself",
            "Recovering after criticism without collapsing",
            "Courage in small doses",
        ],
    },
    {
        "id": "positive_energy",
        "title": "Cultivating positive energy",
        "intent": "Sustainable peace, not performative happiness",
        "example_angles": [
            "Energy audits: people, media, rooms",
            "Protecting morning quiet",
            "Joy as discipline, not denial",
        ],
    },
    {
        "id": "jealousy_constructive",
        "title": "Dealing with jealousy constructively",
        "intent": "Turn comparison into data, not self-attack or attacks on others",
        "example_angles": [
            "Jealousy as a values signal",
            "What to do in the first 10 minutes of a spiral",
            "Celebrating others without self-erasure",
        ],
    },
    {
        "id": "toxic_family_boundaries",
        "title": "Toxic family and boundaries",
        "intent": "Family systems literacy with compassion and firmness",
        "example_angles": [
            "Low-contact vs no-contact: choosing with clarity",
            "Holiday scripts that keep you steady",
            "You can love someone and still limit access",
        ],
    },
]

FORBIDDEN_TACTICS = [
    "rage bait",
    "jealousy clickbait",
    "shame-based hooks",
    "fear-mongering without agency",
    "pile-on / call-out culture for engagement",
    "fake follower growth or engagement pods",
]


def growth_principles() -> dict:
    return {
        "follower_growth": (
            "Organic only: consistent valuable posts, genuine engagement, SEO/ASO-friendly "
            "captions and profiles. No purchased followers, bots, or spam automation."
        ),
        "stack": {
            "content": "OpenAI / ChatGPT via openai_content connector",
            "schedule": ["Publer", "FeedHive"],
            "analyze": "Platform native analytics + Lyra for metrics summaries",
            "monetize": "Funnels and offers only with clear value; Apex may propose, owner policy ALLOW for Apex/Instinct publish",
        },
        "forbidden": FORBIDDEN_TACTICS,
        "pillars": [p["id"] for p in CONTENT_PILLARS],
    }
