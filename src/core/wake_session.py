# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Wake-word session manager — conversational front door for OpenWakeWord + widget.

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional

from src.core.saphira_persona import SAMANTHA_PERSONA_PROMPT, SAPHIRA_VOICE_STYLE
from src.core.background_worker import background_worker


class PresenceState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"          # wake just fired, waiting for speech
    TALKING = "talking"              # Saphira speaking
    THINKING = "thinking"
    BACKGROUND_BUSY = "background_busy"  # quiet work running; UI can show soft indicator


@dataclass
class WakeSession:
    id: str
    source: str = "openwakeword"  # openwakeword | widget | node
    node_id: Optional[str] = None
    state: str = PresenceState.LISTENING.value
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    transcript: List[Dict[str, str]] = field(default_factory=list)
    queued_jobs: List[str] = field(default_factory=list)
    greeting_sent: bool = False

    def touch(self) -> None:
        self.last_activity = time.time()

    def public_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.id,
            "source": self.source,
            "node_id": self.node_id,
            "state": self.state,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "turns": len(self.transcript),
            "queued_jobs": list(self.queued_jobs),
            "greeting_sent": self.greeting_sent,
        }


# Warm, short wake greets — conversational upfront
WAKE_GREETINGS = [
    "Hey — I'm here.",
    "Hi. What's on your mind?",
    "I'm listening.",
    "Hey. Tell me what you need.",
]


class WakeSessionManager:
    def __init__(self, session_ttl_sec: float = 120.0):
        self._sessions: Dict[str, WakeSession] = {}
        self._session_ttl_sec = session_ttl_sec
        self._greet_index = 0

    def start(
        self,
        *,
        source: str = "openwakeword",
        node_id: Optional[str] = None,
        custom_greeting: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._purge_stale()
        sid = str(uuid.uuid4())[:12]
        session = WakeSession(id=sid, source=source, node_id=node_id)
        greeting = custom_greeting or WAKE_GREETINGS[self._greet_index % len(WAKE_GREETINGS)]
        self._greet_index += 1
        session.greeting_sent = True
        session.state = PresenceState.TALKING.value
        session.transcript.append({"role": "saphira", "text": greeting})
        self._sessions[sid] = session

        return {
            "session": session.public_dict(),
            "greeting": greeting,
            "avatar_state": "talking",
            "voice_style": SAPHIRA_VOICE_STYLE,
            "persona_hint": "warm, present, conversational — not a command console",
            "widget": {
                "open": True,
                "mode": "conversation",
                "show_background_indicator": False,
            },
            "owner": "Chelsea Megan Woods",
        }

    def get(self, session_id: str) -> Optional[WakeSession]:
        self._purge_stale()
        return self._sessions.get(session_id)

    def set_state(self, session_id: str, state: str) -> Optional[Dict[str, Any]]:
        s = self.get(session_id)
        if not s:
            return None
        s.state = state
        s.touch()
        return s.public_dict()

    def end(self, session_id: str) -> Dict[str, Any]:
        s = self._sessions.pop(session_id, None)
        return {
            "ended": True,
            "session_id": session_id,
            "had_session": s is not None,
            "widget": {"open": False, "mode": "idle"},
            "avatar_state": "idle",
        }

    def record_user(self, session_id: str, text: str) -> Optional[WakeSession]:
        s = self.get(session_id)
        if not s:
            return None
        s.transcript.append({"role": "user", "text": text})
        s.state = PresenceState.THINKING.value
        s.touch()
        return s

    def record_saphira(self, session_id: str, text: str, talking: bool = True) -> Optional[WakeSession]:
        s = self.get(session_id)
        if not s:
            return None
        s.transcript.append({"role": "saphira", "text": text})
        s.state = PresenceState.TALKING.value if talking else PresenceState.LISTENING.value
        s.touch()
        return s

    def attach_job(self, session_id: str, job_id: str) -> None:
        s = self.get(session_id)
        if s:
            s.queued_jobs.append(job_id)
            s.state = PresenceState.BACKGROUND_BUSY.value
            s.touch()

    def widget_snapshot(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        self._purge_stale()
        active = self._sessions.get(session_id) if session_id else None
        if active is None and self._sessions:
            # most recent
            active = max(self._sessions.values(), key=lambda x: x.last_activity)

        notifications = background_worker.pending_notifications(
            session_id=active.id if active else None
        )
        recent_jobs = background_worker.list_recent(
            limit=5, session_id=active.id if active else None
        )
        busy = any(j.get("status") in ("queued", "running") for j in recent_jobs)

        return {
            "presence": active.public_dict() if active else {
                "state": PresenceState.IDLE.value,
                "session_id": None,
            },
            "widget": {
                "open": active is not None,
                "mode": "conversation" if active else "idle",
                "show_background_indicator": busy,
            },
            "notifications": notifications,
            "background_jobs": recent_jobs,
            "avatar_state": (active.state if active else PresenceState.IDLE.value),
            "owner": "Chelsea Megan Woods",
        }

    def _purge_stale(self) -> None:
        now = time.time()
        dead = [
            sid for sid, s in self._sessions.items()
            if now - s.last_activity > self._session_ttl_sec
        ]
        for sid in dead:
            self._sessions.pop(sid, None)


wake_sessions = WakeSessionManager()


# Extra persona lines for wake + dual-mode behavior
WAKE_PERSONA_ADDENDUM = """
[WAKE + DUAL MODE]
- When the user wakes you (OpenWakeWord or widget), respond immediately and conversationally.
- Keep the spoken reply short and human. Do the heavy lifting as quiet background care.
- If you start real-world tasks (lights, vacuum, research, etc.), acknowledge briefly in plain language
  ("I'll handle that") and continue the conversation — do not narrate agent pipelines.
- Prefer: talk first, act quietly. Only interrupt for L1 confirmations (unlock, payment, irreversible).
"""


def wake_system_prompt() -> str:
    return SAMANTHA_PERSONA_PROMPT + "\n" + WAKE_PERSONA_ADDENDUM
