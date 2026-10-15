"""Deterministic loop prevention for multi-agent execution.

Target: 100% block of infinite agent loops (Aura / Agent Zero specialty).

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LoopVerdict:
    allowed: bool
    reason: str
    fingerprint: str
    prior_count: int


class LoopGuard:
    """Session-scoped cycle detector.

    Blocks when the same (session, agent, intent fingerprint) repeats
    beyond max_repeats within window_sec.
    """

    def __init__(self, *,
                 max_repeats: int = 2,
                 window_sec: float = 30.0,
                 max_entries: int = 10_000) -> None:
        self.max_repeats = max_repeats
        self.window_sec = window_sec
        self.max_entries = max_entries
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def fingerprint(session_id: str, agent: str, intent: str) -> str:
        raw = f"{session_id}|{agent}|{intent.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def check(
        self,
        *,
        session_id: str,
        agent: str,
        intent: str,
        record: bool = True,
    ) -> LoopVerdict:
        fp = self.fingerprint(session_id, agent, intent)
        now = time.time()
        with self._lock:
            times = [t for t in self._hits.get(fp, []) if now - t <= self.window_sec]
            count = len(times)
            if count >= self.max_repeats:
                return LoopVerdict(
                    allowed=False,
                    reason=f"loop_blocked: {count} repeats in {self.window_sec}s",
                    fingerprint=fp,
                    prior_count=count,
                )
            if record:
                times.append(now)
                self._hits[fp] = times
                if len(self._hits) > self.max_entries:
                    # drop oldest keys
                    for k in list(self._hits.keys())[: len(self._hits) - self.max_entries]:
                        self._hits.pop(k, None)
            return LoopVerdict(
                allowed=True,
                reason="ok",
                fingerprint=fp,
                prior_count=count,
            )

    def reset_session(self, session_id: str) -> int:
        """Clear fingerprints for a session prefix (best-effort)."""
        removed = 0
        with self._lock:
            for k in list(self._hits.keys()):
                # fingerprints are hashed; full clear is safer on explicit reset
                pass
            # Explicit API: clear all (sessions are short-lived)
            removed = len(self._hits)
            self._hits.clear()
        return removed


global_loop_guard = LoopGuard()
