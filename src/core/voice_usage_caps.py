# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies
#
# Free-tier voice usage caps — protect margin against uncapped real-time audio costs.

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


# Defaults are intentionally conservative for public / free demos.
# Override with environment variables in production.
DEFAULT_SESSION_MINUTES = float(os.getenv("SAPHIRA_VOICE_SESSION_CAP_MINUTES", "8.0"))
DEFAULT_DAILY_MINUTES = float(os.getenv("SAPHIRA_VOICE_DAILY_CAP_MINUTES", "20.0"))
DEFAULT_HARD_STOP = os.getenv("SAPHIRA_VOICE_HARD_STOP", "true").lower() in ("1", "true", "yes")


@dataclass
class VoiceUsageState:
    user_id: str
    session_seconds_used: float = 0.0
    daily_seconds_used: float = 0.0
    session_started_at: float = field(default_factory=time.time)
    last_reset_day: str = field(default_factory=lambda: time.strftime("%Y-%m-%d"))


class VoiceUsageCapper:
    """
    In-memory (or later Redis-backed) tracker for free-tier voice minutes.

    Call `can_start` / `record` around every real-time voice segment.
    When a limit is hit, return a clear, user-facing message and stop the stream.
    """

    def __init__(
        self,
        session_cap_minutes: float = DEFAULT_SESSION_MINUTES,
        daily_cap_minutes: float = DEFAULT_DAILY_MINUTES,
        hard_stop: bool = DEFAULT_HARD_STOP,
    ) -> None:
        self.session_cap_seconds = session_cap_minutes * 60.0
        self.daily_cap_seconds = daily_cap_minutes * 60.0
        self.hard_stop = hard_stop
        self._state: Dict[str, VoiceUsageState] = {}

    def _get(self, user_id: str) -> VoiceUsageState:
        today = time.strftime("%Y-%m-%d")
        st = self._state.get(user_id)
        if st is None:
            st = VoiceUsageState(user_id=user_id)
            self._state[user_id] = st
            return st
        if st.last_reset_day != today:
            st.daily_seconds_used = 0.0
            st.last_reset_day = today
        return st

    def can_start(self, user_id: str) -> tuple[bool, Optional[str]]:
        """Return (allowed, human_message_if_blocked)."""
        st = self._get(user_id)
        if st.daily_seconds_used >= self.daily_cap_seconds:
            return False, (
                "You've reached today's free voice limit. "
                "Text is still fully available — or upgrade for more live minutes."
            )
        if st.session_seconds_used >= self.session_cap_seconds:
            return False, (
                "This free voice session has reached its limit. "
                "Start a new session later or continue in text."
            )
        return True, None

    def record(self, user_id: str, seconds: float) -> None:
        """Accumulate usage after a segment completes."""
        if seconds <= 0:
            return
        st = self._get(user_id)
        st.session_seconds_used += seconds
        st.daily_seconds_used += seconds

    def remaining(self, user_id: str) -> dict:
        st = self._get(user_id)
        return {
            "session_remaining_seconds": max(0.0, self.session_cap_seconds - st.session_seconds_used),
            "daily_remaining_seconds": max(0.0, self.daily_cap_seconds - st.daily_seconds_used),
            "hard_stop": self.hard_stop,
        }


# Singleton for simple FastAPI dependency injection
voice_capper = VoiceUsageCapper()
