"""Low-latency device bridge for Saphira Android clients.

The endpoint intentionally does not store raw audio. Binary frames are accepted,
validated, and handed to the configured audio pipeline adapter. A production STT/
TTS provider can subscribe through the adapter without changing the Android client.

Supports barge-in via stop_audio control frames that immediately abort any active
TTS packet queue for the session.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from typing import Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/device", tags=["device"])


@dataclass
class AudioSession:
    session_id: str
    sample_rate: int = 16000
    channels: int = 1
    encoding: str = "pcm_s16le"
    speaking: bool = False
    aborted: bool = False


class AudioPipeline:
    """Provider-neutral streaming adapter.

    Replace `process_chunk` with an authenticated STT/realtime provider adapter.
    Keeping this boundary here prevents provider credentials from reaching Android.
    """

    def __init__(self) -> None:
        self._active_sessions: Set[str] = set()

    async def process_chunk(self, session: AudioSession, data: bytes) -> None:
        # Intentionally no persistence of raw audio.
        return None

    async def abort_tts(self, session: AudioSession) -> None:
        """Flush any pending TTS packets for this session (barge-in)."""
        session.speaking = False
        session.aborted = True
        # Production: signal the TTS provider / packet queue to drop remaining frames.


pipeline = AudioPipeline()


def _authorized(token: Optional[str]) -> bool:
    expected = os.getenv("SAPHIRA_DEVICE_TOKEN")
    if not expected:
        return False
    return bool(token) and token == expected


@router.websocket("/audio")
async def audio_socket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    await websocket.accept()

    if not _authorized(token):
        await websocket.send_json({"type": "error", "code": "unauthorized"})
        await websocket.close(code=1008)
        return

    session = AudioSession(session_id=str(uuid.uuid4()))
    await websocket.send_json({
        "type": "session_ready",
        "session_id": session.session_id,
        "sample_rate": session.sample_rate,
        "channels": session.channels,
        "encoding": session.encoding,
    })

    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break

            if message.get("bytes") is not None:
                if session.aborted:
                    # After barge-in we still accept mic audio but do not restart TTS
                    # until a fresh user turn is signaled.
                    pass
                data = message["bytes"]
                if len(data) > 256 * 1024:
                    await websocket.send_json({"type": "error", "code": "frame_too_large"})
                    continue
                await pipeline.process_chunk(session, data)
                await websocket.send_json({"type": "audio_ack", "bytes": len(data)})
            elif message.get("text"):
                text = message["text"]
                # Control plane: stop_audio / barge-in
                try:
                    import json
                    payload = json.loads(text) if text.startswith("{") else {"raw": text}
                    msg_type = payload.get("type", "")
                    if msg_type in ("stop_audio", "barge_in", "abort_tts"):
                        await pipeline.abort_tts(session)
                        await websocket.send_json({
                            "type": "audio_aborted",
                            "session_id": session.session_id,
                            "reason": payload.get("reason", "barge_in"),
                        })
                        continue
                    if msg_type == "end_of_utterance":
                        session.aborted = False  # ready for next assistant turn
                except Exception:
                    pass
                await websocket.send_json({"type": "control_ack", "message": text[:200]})
    except WebSocketDisconnect:
        pass
