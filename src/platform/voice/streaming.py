"""Streaming voice duplex protocol and session state."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time
import uuid


class AvatarState(str, Enum):
    IDLE = "idle"
    TALKING = "talking"
    THINKING = "thinking"
    CONFIRM = "confirm"
    GLOW = "glow"


@dataclass
class VoiceSession:
    session_id: str
    tenant_id: str
    user_id: str
    avatar_state: AvatarState = AvatarState.IDLE
    barge_in_enabled: bool = True
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VoiceSessionManager:
    def __init__(self) -> None:
        self._sessions: Dict[str, VoiceSession] = {}

    def create(self, tenant_id: str, user_id: str, **meta: Any) -> VoiceSession:
        sid = str(uuid.uuid4())
        sess = VoiceSession(session_id=sid, tenant_id=tenant_id, user_id=user_id, metadata=dict(meta))
        self._sessions[sid] = sess
        return sess

    def set_state(self, session_id: str, state: AvatarState) -> Optional[VoiceSession]:
        sess = self._sessions.get(session_id)
        if not sess:
            return None
        sess.avatar_state = state
        return sess

    def get(self, session_id: str) -> Optional[VoiceSession]:
        return self._sessions.get(session_id)

    def end(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None


voice_sessions = VoiceSessionManager()
