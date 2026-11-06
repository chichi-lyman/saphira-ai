"""
src/tools/ambient/trivia.py
Spontaneous topic-based trivia for Saphira AI
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TriviaQuestion:
    question: str
    answer: str
    difficulty: str = "medium"
    source_note: str = ""


@dataclass
class TriviaRound:
    topic: str
    questions: list[TriviaQuestion] = field(default_factory=list)
    score: int = 0
    current_index: int = 0


_SEED: dict[str, list[tuple[str, str]]] = {
    "space": [
        ("Which planet is known as the Red Planet?", "Mars"),
        ("What is the name of our galaxy?", "Milky Way"),
        ("Who was the first human in space?", "Yuri Gagarin"),
    ],
    "history": [
        ("In which year did the Titanic sink?", "1912"),
        ("Who was the first President of the United States?", "George Washington"),
    ],
    "science": [
        ("What is the chemical symbol for gold?", "Au"),
        ("What force keeps planets in orbit around the Sun?", "Gravity"),
    ],
    "general": [
        ("How many continents are there?", "7"),
        ("What is the largest ocean on Earth?", "Pacific Ocean"),
    ],
}


def start_trivia(topic: str, num_questions: int = 5) -> TriviaRound:
    topic_key = topic.lower().strip()
    pool = _SEED.get(topic_key) or _SEED["general"]
    for key, questions in _SEED.items():
        if key in topic_key or topic_key in key:
            pool = questions
            break

    selected = random.sample(pool, k=min(num_questions, len(pool)))
    questions = [
        TriviaQuestion(question=q, answer=a, source_note="seed")
        for q, a in selected
    ]
    return TriviaRound(topic=topic, questions=questions)


def check_answer(round_: TriviaRound, user_answer: str) -> dict:
    if round_.current_index >= len(round_.questions):
        return {"ok": False, "reason": "round_complete"}

    q = round_.questions[round_.current_index]
    correct = user_answer.strip().lower() == q.answer.strip().lower()
    if correct:
        round_.score += 1
    round_.current_index += 1

    return {
        "ok": True,
        "correct": correct,
        "expected": q.answer,
        "score": round_.score,
        "remaining": len(round_.questions) - round_.current_index,
        "finished": round_.current_index >= len(round_.questions),
    }


async def generate_trivia_from_research(topic: str, synthesis_brief: str, num: int = 5) -> TriviaRound:
    return start_trivia(topic, num_questions=num)
