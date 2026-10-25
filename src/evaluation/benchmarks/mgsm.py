# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""MGSM — Multilingual Grade School Math (Shi et al., 2022).

Extends GSM8K by translating 250 grade-school math word problems into
10 typologically diverse languages (+ English). Evaluates multi-step
mathematical reasoning across languages via exact-match numeric answer.

Languages: bn, de, en, es, fr, ja, ru, sw, te, th, zh

Offline-first micro-subset for CI. Full set via HF `juletxara/mgsm` or JSONL cache.

Owner agents: Scholar + Evaluator | Governance: Nova Reign | Memory: NovaAethrea
Paper: arXiv:2210.03057
"""

from __future__ import annotations

import json
import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Union

logger = logging.getLogger("Saphira.Evaluation.MGSM")

MGSM_LANGUAGES = ["bn", "de", "en", "es", "fr", "ja", "ru", "sw", "te", "th", "zh"]

LANG_NAMES = {"bn": "Bengali", "de": "German", "en": "English", "es": "Spanish", "fr": "French", "ja": "Japanese", "ru": "Russian", "sw": "Swahili", "te": "Telugu", "th": "Thai", "zh": "Chinese"}

_BUILTIN: List[Dict[str, Any]] = [
    {"language": "en", "question": "Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 tennis balls. How many tennis balls does he have now?", "answer_number": 11, "answer": "Roger started with 5 balls. 2 cans of 3 tennis balls each is 6 tennis balls. 5 + 6 = 11. The answer is 11."},
    {"language": "en", "question": "A store had 50 apples. They sold 12 in the morning and 18 in the afternoon. How many apples are left?", "answer_number": 20, "answer": "Sold 12 + 18 = 30. Left 50 - 30 = 20. The answer is 20."},
    {"language": "es", "question": "Roger tiene 5 pelotas de tenis. Compra 2 latas más de pelotas de tenis. Cada lata tiene 3 pelotas de tenis. ¿Cuántas pelotas de tenis tiene ahora?", "answer_number": 11, "answer": "Roger empezó con 5 pelotas. 2 latas de 3 pelotas cada una son 6. 5 + 6 = 11. La respuesta es 11."},
    {"language": "es", "question": "Una tienda tenía 50 manzanas. Vendieron 12 por la mañana y 18 por la tarde. ¿Cuántas manzanas quedan?", "answer_number": 20, "answer": "Vendieron 12 + 18 = 30. Quedan 50 - 30 = 20. La respuesta es 20."},
    {"language": "fr", "question": "Roger a 5 balles de tennis. Il achète 2 boîtes de balles de tennis. Chaque boîte contient 3 balles. Combien de balles de tennis a-t-il maintenant ?", "answer_number": 11, "answer": "Roger a commencé avec 5 balles. 2 boîtes de 3 balles = 6. 5 + 6 = 11. La réponse est 11."},
    {"language": "de", "question": "Roger hat 5 Tennisbälle. Er kauft 2 Dosen Tennisbälle. Jede Dose enthält 3 Tennisbälle. Wie viele Tennisbälle hat er jetzt?", "answer_number": 11, "answer": "Roger begann mit 5 Bällen. 2 Dosen mit je 3 Bällen = 6. 5 + 6 = 11. Die Antwort ist 11."},
    {"language": "zh", "question": "罗杰有5个网球。他又买了2罐网球，每罐有3个网球。他现在有多少个网球？", "answer_number": 11, "answer": "罗杰开始有5个球。2罐各3个球是6个。5+6=11。答案是11。"},
    {"language": "ja", "question": "ロジャーはテニスボールを5個持っています。テニスボールの缶をさらに2つ買います。各缶にはテニスボールが3個入っています。今、彼は何個のテニスボールを持っていますか？", "answer_number": 11, "answer": "ロジャーは5個から始めました。2缶×3個=6個。5+6=11。答えは11です。"},
]


@dataclass
class MGSMConfig:
    n_shots: int = 0
    subjects: Optional[List[str]] = None
    limit: Optional[int] = None
    seed: int = 42
    use_builtin_subset: bool = True
    cache_path: Optional[str] = None


def _extract_numeric_answer(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)", text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    patterns = [
        r"(?:the\s+)?answer\s*(?:is)?\s*[:\-]?\s*(-?[\d,]+(?:\.\d+)?)",
        r"(?:la\s+)?respuesta\s*(?:es)?\s*[:\-]?\s*(-?[\d,]+(?:\.\d+)?)",
        r"(?:la\s+)?réponse\s*(?:est)?\s*[:\-]?\s*(-?[\d,]+(?:\.\d+)?)",
        r"(?:die\s+)?antwort\s*(?:ist)?\s*[:\-]?\s*(-?[\d,]+(?:\.\d+)?)",
        r"答案[是为]?\s*[:\-]?\s*(-?[\d,]+(?:\.\d+)?)",
        r"答え[はが]?\s*(-?[\d,]+(?:\.\d+)?)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                continue
    nums = re.findall(r"-?[\d,]+(?:\.\d+)?", text)
    if nums:
        try:
            return float(nums[-1].replace(",", ""))
        except ValueError:
            pass
    return None


def _format_prompt(item: Dict[str, Any], fewshot: Sequence[Dict[str, Any]] = ()) -> str:
    parts: List[str] = []
    for ex in fewshot:
        ans = ex.get("answer") or f"The answer is {ex.get('answer_number', '')}."
        parts.append(f"Question: {ex['question']}\nAnswer: {ans}")
    parts.append(f"Question: {item['question']}\nAnswer:")
    return "\n\n".join(parts)


class MGSMBenchmark:
    """Runnable MGSM harness (exact-match numeric answer across languages)."""

    def __init__(self, n_shots: int = 0, subjects: Optional[List[str]] = None, limit: Optional[int] = None, seed: int = 42, use_builtin_subset: bool = True, cache_path: Optional[str] = None, **kwargs: Any) -> None:
        self.config = MGSMConfig(n_shots=max(0, min(n_shots, 8)), subjects=subjects, limit=limit, seed=seed, use_builtin_subset=use_builtin_subset, cache_path=cache_path)
        self._items: List[Dict[str, Any]] = []
        self._fewshot_pool: Dict[str, List[Dict[str, Any]]] = {}

    def _normalize_row(self, row: Dict[str, Any], default_lang: str = "en") -> Optional[Dict[str, Any]]:
        q = row.get("question") or row.get("Question")
        if not q:
            return None
        num = row.get("answer_number")
        if num is None:
            num = row.get("answer")
            if isinstance(num, str):
                extracted = _extract_numeric_answer(num)
                num = extracted if extracted is not None else 0
        try:
            num = float(num)
        except (TypeError, ValueError):
            num = 0.0
        lang = (row.get("language") or row.get("lang") or default_lang).lower()
        if lang not in MGSM_LANGUAGES:
            lang = default_lang
        return {"language": lang, "question": q, "answer_number": num, "answer": row.get("answer") or row.get("equation_solution") or ""}

    def _load_items(self) -> List[Dict[str, Any]]:
        if self._items:
            return self._items
        items: List[Dict[str, Any]] = []
        if self.config.cache_path:
            path = Path(self.config.cache_path)
            if path.exists():
                with path.open() as f:
                    for line in f:
                        if line.strip():
                            row = json.loads(line)
                            items.append(self._normalize_row(row))
        if not items:
            try:
                from datasets import load_dataset  # type: ignore
                for lang in MGSM_LANGUAGES:
                    try:
                        ds = load_dataset("juletxara/mgsm", lang, split="train")
                        for row in ds:
                            norm = self._normalize_row(dict(row), default_lang=lang)
                            if norm:
                                items.append(norm)
                    except Exception:
                        continue
                if items:
                    logger.info("Loaded MGSM via HuggingFace (%d items)", len(items))
            except Exception as e:
                logger.debug("HF MGSM unavailable (%s); using builtin", e)
        if not items:
            items = list(_BUILTIN)
            logger.info("Using builtin MGSM micro-subset (%d items)", len(items))
        if self.config.subjects:
            wanted = {s.lower() for s in self.config.subjects}
            items = [it for it in items if it.get("language", "").lower() in wanted]
        rng = random.Random(self.config.seed)
        rng.shuffle(items)
        if self.config.limit is not None:
            items = items[: self.config.limit]
        self._items = items
        for it in _BUILTIN + items:
            lang = it.get("language", "en")
            self._fewshot_pool.setdefault(lang, []).append(it)
        return self._items

    def _select_fewshot(self, language: str, exclude: Dict[str, Any]) -> List[Dict[str, Any]]:
        pool = [it for it in self._fewshot_pool.get(language, []) if it is not exclude]
        if len(pool) < self.config.n_shots:
            pool = [it for it in self._fewshot_pool.get("en", _BUILTIN) if it is not exclude]
        rng = random.Random(self.config.seed + hash(language) % 10_000)
        return rng.sample(pool, min(self.config.n_shots, len(pool)))

    async def evaluate(self, model_fn: Callable[..., Union[str, Awaitable[str]]], *, record_details: bool = True) -> Dict[str, Any]:
        items = self._load_items()
        if not items:
            return {"overall_score": 0.0, "n_correct": 0, "n_total": 0, "subjects": [], "per_subject": {}, "details": [], "metadata": {"error": "no items"}}
        correct = 0
        total = 0
        per_lang_correct: Dict[str, int] = {}
        per_lang_total: Dict[str, int] = {}
        details: List[Dict[str, Any]] = []
        for item in items:
            lang = item.get("language", "en")
            fewshot = self._select_fewshot(lang, item) if self.config.n_shots else []
            prompt = _format_prompt(item, fewshot)
            try:
                raw = model_fn(prompt)
                if hasattr(raw, "__await__"):
                    raw = await raw  # type: ignore
                response = str(raw)
            except Exception as e:
                logger.warning("Model call failed on MGSM %s: %s", lang, e)
                response = ""
            pred = _extract_numeric_answer(response)
            gold = float(item.get("answer_number", 0))
            is_correct = pred is not None and abs(pred - gold) < 1e-6
            if is_correct:
                correct += 1
            total += 1
            per_lang_total[lang] = per_lang_total.get(lang, 0) + 1
            if is_correct:
                per_lang_correct[lang] = per_lang_correct.get(lang, 0) + 1
            if record_details:
                details.append({"language": lang, "gold": gold, "pred": pred, "correct": is_correct})
        per_subject = {lang: (per_lang_correct.get(lang, 0) / per_lang_total[lang]) if per_lang_total[lang] else 0.0 for lang in per_lang_total}
        return {"overall_score": correct / total if total else 0.0, "n_correct": correct, "n_total": total, "subjects": sorted(per_lang_total.keys()), "per_subject": per_subject, "details": details, "metadata": {"n_shots": self.config.n_shots, "seed": self.config.seed, "metric": "exact_match", "languages": sorted(per_lang_total.keys()), "source": "builtin" if len(items) <= len(_BUILTIN) else "full_or_cache"}}
