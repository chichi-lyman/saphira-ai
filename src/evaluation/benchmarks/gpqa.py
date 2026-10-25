# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Nova Umbrella Ecosystem / Saphira AI

"""GPQA — Graduate-Level Google-Proof Q&A (Rein et al., 2023).

448 multiple-choice questions (main set) written by domain experts in
biology, physics, and chemistry. Designed so PhD-level experts score ~65–81%
while skilled non-experts with web access score ~22–34% ("Google-proof").

Primary subsets: GPQA main (448), GPQA Diamond (198).
Format: 4-choice MCQ. Metric: accuracy (exact match on A/B/C/D).

Offline-first micro-subset for CI. Full set via HF `Idavidrein/gpqa` or JSONL cache.

Owner agents: Scholar + Evaluator | Governance: Nova Reign | Memory: NovaAethrea
Paper: arXiv:2311.12022
"""

from __future__ import annotations

import json
import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Union

logger = logging.getLogger("Saphira.Evaluation.GPQA")

GPQA_DOMAINS = ["biology", "chemistry", "physics"]

_BUILTIN: List[Dict[str, Any]] = [
    {"id": "gpqa_builtin_bio_1", "domain": "biology", "question": "In eukaryotic gene expression, which modification of histone H3 is most strongly associated with transcriptional activation of euchromatic regions?", "choices": ["Trimethylation of lysine 9 (H3K9me3)", "Trimethylation of lysine 27 (H3K27me3)", "Acetylation of lysine 27 (H3K27ac)", "Ubiquitination of lysine 119 on H2A"], "answer": 2},
    {"id": "gpqa_builtin_bio_2", "domain": "biology", "question": "A mutation that eliminates the Shine-Dalgarno sequence in a bacterial mRNA would most directly impair which step of gene expression?", "choices": ["Transcription initiation by RNA polymerase", "Ribosome binding and translation initiation", "mRNA polyadenylation", "Splicing of introns"], "answer": 1},
    {"id": "gpqa_builtin_chem_1", "domain": "chemistry", "question": "For an SN1 reaction of a tertiary alkyl halide, which factor most strongly increases the rate of the rate-determining step?", "choices": ["A more nucleophilic attacking species", "A higher concentration of the nucleophile", "A polar protic solvent that stabilizes the carbocation intermediate", "A less substituted alkyl halide substrate"], "answer": 2},
    {"id": "gpqa_builtin_chem_2", "domain": "chemistry", "question": "In 13C NMR spectroscopy, which carbon environment typically appears furthest downfield (largest chemical shift)?", "choices": ["Alkyl carbon attached only to other carbons and hydrogens", "Carbonyl carbon of a ketone or aldehyde", "Aromatic carbon in benzene", "Alkyne carbon"], "answer": 1},
    {"id": "gpqa_builtin_phys_1", "domain": "physics", "question": "In the quantum harmonic oscillator, the energy eigenvalues are E_n = ħω(n + 1/2). What is the expectation value of the potential energy in an energy eigenstate |n⟩?", "choices": ["ħω(n + 1/2)", "½ ħω(n + 1/2)", "ħω n", "0"], "answer": 1},
    {"id": "gpqa_builtin_phys_2", "domain": "physics", "question": "For a particle in a one-dimensional infinite square well from 0 to L, which statement about the ground-state wavefunction ψ_1(x) is correct?", "choices": ["ψ_1 has one node inside (0, L)", "ψ_1 is odd with respect to x = L/2", "ψ_1 is even with respect to x = L/2 and has no nodes inside (0, L)", "The probability density |ψ_1|² is uniform across the well"], "answer": 2},
    {"id": "gpqa_builtin_phys_3", "domain": "physics", "question": "In special relativity, a particle of rest mass m has total energy E and momentum p. Which relation is always true?", "choices": ["E = p c", "E² = (p c)² + (m c²)²", "E = m c² + p² / (2m)", "p = m v with v unrestricted"], "answer": 1},
    {"id": "gpqa_builtin_chem_3", "domain": "chemistry", "question": "According to the 18-electron rule, which of the following organometallic complexes is most likely to be stable as a neutral 18-electron species?", "choices": ["Ni(CO)₃", "Fe(CO)₅", "Cr(CO)₄", "Mn(CO)₆"], "answer": 1},
]


@dataclass
class GPQAConfig:
    n_shots: int = 0
    subjects: Optional[List[str]] = None
    limit: Optional[int] = None
    seed: int = 42
    use_builtin_subset: bool = True
    cache_path: Optional[str] = None
    prefer_diamond: bool = True


def _extract_choice(text: str) -> Optional[int]:
    if not text:
        return None
    text = text.strip().upper()
    m = re.search(r"\b([ABCD])\b", text)
    if m:
        return ord(m.group(1)) - ord("A")
    m = re.search(r"\b([0-3])\b", text)
    if m:
        return int(m.group(1))
    m = re.search(r"\b([1-4])\b", text)
    if m:
        return int(m.group(1)) - 1
    m = re.search(r"ANSWER\s*[:\-]?\s*([ABCD])", text)
    if m:
        return ord(m.group(1)) - ord("A")
    return None


def _format_prompt(item: Dict[str, Any], fewshot: Sequence[Dict[str, Any]] = ()) -> str:
    parts: List[str] = []
    for ex in fewshot:
        parts.append(_format_single(ex, include_answer=True))
    parts.append(_format_single(item, include_answer=False))
    parts.append("Answer with the letter of the correct choice only (A, B, C, or D).")
    parts.append("Answer:")
    return "\n\n".join(parts)


def _format_single(item: Dict[str, Any], include_answer: bool) -> str:
    lines = [f"Question: {item['question']}"]
    for i, c in enumerate(item["choices"]):
        lines.append(f"{chr(65 + i)}. {c}")
    if include_answer:
        lines.append(f"Answer: {chr(65 + item['answer'])}")
    return "\n".join(lines)


class GPQABenchmark:
    """Runnable GPQA evaluation harness (accuracy on 4-choice graduate science MCQ)."""

    def __init__(self, n_shots: int = 0, subjects: Optional[List[str]] = None, limit: Optional[int] = None, seed: int = 42, use_builtin_subset: bool = True, cache_path: Optional[str] = None, prefer_diamond: bool = True, **kwargs: Any) -> None:
        self.config = GPQAConfig(n_shots=max(0, min(n_shots, 5)), subjects=subjects, limit=limit, seed=seed, use_builtin_subset=use_builtin_subset, cache_path=cache_path, prefer_diamond=prefer_diamond)
        self._items: List[Dict[str, Any]] = []
        self._fewshot_pool: Dict[str, List[Dict[str, Any]]] = {}

    def _normalize_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        q = row.get("question") or row.get("Question") or row.get("Pre-Revision Question")
        if not q:
            return None
        correct = row.get("correct_answer") or row.get("Correct Answer") or row.get("answer")
        incorrects = []
        for k in ("Incorrect Answer 1", "Incorrect Answer 2", "Incorrect Answer 3", "incorrect_answer_1", "incorrect_answer_2", "incorrect_answer_3"):
            if row.get(k):
                incorrects.append(row[k])
        if correct is None or len(incorrects) < 3:
            choices = row.get("choices")
            answer = row.get("answer")
            if choices and answer is not None:
                domain = (row.get("domain") or row.get("High-level domain") or "unknown").lower()
                return {"id": str(row.get("id") or row.get("Record ID") or hash(q) % 10**8), "domain": domain if domain in GPQA_DOMAINS else "unknown", "question": q, "choices": list(choices), "answer": int(answer) if not isinstance(answer, int) else answer}
            return None
        choices = [correct] + incorrects[:3]
        rng = random.Random(hash(q) % (2**32))
        order = list(range(4))
        rng.shuffle(order)
        shuffled = [choices[i] for i in order]
        answer_idx = order.index(0)
        domain = (row.get("domain") or row.get("High-level domain") or row.get("Subdomain") or "unknown")
        domain = str(domain).lower()
        if "bio" in domain:
            domain = "biology"
        elif "chem" in domain:
            domain = "chemistry"
        elif "phys" in domain:
            domain = "physics"
        else:
            domain = domain if domain in GPQA_DOMAINS else "unknown"
        return {"id": str(row.get("id") or row.get("Record ID") or hash(q) % 10**8), "domain": domain, "question": q, "choices": shuffled, "answer": answer_idx}

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
                            norm = self._normalize_row(row) if "choices" not in row else row
                            if norm:
                                items.append(norm)
        if not items:
            try:
                from datasets import load_dataset  # type: ignore
                config_name = "gpqa_diamond" if self.config.prefer_diamond else "gpqa_main"
                try:
                    ds = load_dataset("Idavidrein/gpqa", config_name, split="train")
                except Exception:
                    ds = load_dataset("Idavidrein/gpqa", "gpqa_main", split="train")
                for row in ds:
                    norm = self._normalize_row(dict(row))
                    if norm:
                        items.append(norm)
                logger.info("Loaded GPQA via HuggingFace (%d items)", len(items))
            except Exception as e:
                logger.debug("HF GPQA unavailable (%s); using builtin", e)
        if not items:
            items = list(_BUILTIN)
            logger.info("Using builtin GPQA micro-subset (%d items)", len(items))
        if self.config.subjects:
            wanted = {s.lower() for s in self.config.subjects}
            items = [it for it in items if it.get("domain", "").lower() in wanted]
        rng = random.Random(self.config.seed)
        rng.shuffle(items)
        if self.config.limit is not None:
            items = items[: self.config.limit]
        self._items = items
        for it in _BUILTIN + items:
            dom = it.get("domain", "unknown")
            self._fewshot_pool.setdefault(dom, []).append(it)
        return self._items

    def _select_fewshot(self, domain: str, exclude: Dict[str, Any]) -> List[Dict[str, Any]]:
        pool = [it for it in self._fewshot_pool.get(domain, []) if it is not exclude]
        if len(pool) < self.config.n_shots:
            pool = [it for it in _BUILTIN if it is not exclude]
        rng = random.Random(self.config.seed + hash(domain) % 10_000)
        return rng.sample(pool, min(self.config.n_shots, len(pool)))

    async def evaluate(self, model_fn: Callable[..., Union[str, Awaitable[str]]], *, record_details: bool = True) -> Dict[str, Any]:
        items = self._load_items()
        if not items:
            return {"overall_score": 0.0, "n_correct": 0, "n_total": 0, "subjects": [], "per_subject": {}, "details": [], "metadata": {"error": "no items"}}
        correct = 0
        total = 0
        per_dom_correct: Dict[str, int] = {}
        per_dom_total: Dict[str, int] = {}
        details: List[Dict[str, Any]] = []
        for item in items:
            fewshot = self._select_fewshot(item.get("domain", "unknown"), item) if self.config.n_shots else []
            prompt = _format_prompt(item, fewshot)
            try:
                raw = model_fn(prompt)
                if hasattr(raw, "__await__"):
                    raw = await raw  # type: ignore
                response = str(raw)
            except Exception as e:
                logger.warning("Model call failed on GPQA %s: %s", item.get("id"), e)
                response = ""
            pred = _extract_choice(response)
            gold = int(item["answer"])
            is_correct = pred is not None and pred == gold
            if is_correct:
                correct += 1
            total += 1
            dom = item.get("domain", "unknown")
            per_dom_total[dom] = per_dom_total.get(dom, 0) + 1
            if is_correct:
                per_dom_correct[dom] = per_dom_correct.get(dom, 0) + 1
            if record_details:
                details.append({"id": item.get("id"), "domain": dom, "gold": gold, "pred": pred, "correct": is_correct})
        per_subject = {d: (per_dom_correct.get(d, 0) / per_dom_total[d]) if per_dom_total[d] else 0.0 for d in per_dom_total}
        return {"overall_score": correct / total if total else 0.0, "n_correct": correct, "n_total": total, "subjects": sorted(per_dom_total.keys()), "per_subject": per_subject, "details": details, "metadata": {"n_shots": self.config.n_shots, "seed": self.config.seed, "metric": "accuracy", "prefer_diamond": self.config.prefer_diamond, "source": "builtin" if len(items) <= len(_BUILTIN) else "full_or_cache"}}
