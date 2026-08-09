"""Low-latency device bridge for Saphira Android clients.

The endpoint intentionally does not store raw audio. Binary frames are accepted,
validated, and handed to the configured audio pipeline adapter. A production STT/
TTS provider can subscribe through the adapter without changing the Android client.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/device", tags=["device"])


@dataclass
class AudioSession:
    session_id: str
    sample_rate: int = 16000
    channels: int = 1
    encoding: str = "pcm_s16le"


class AudioPipeline:
    """Provider-neutral streaming adapter.

    Replace `process_chunk` with an authenticated STT/realtime provider adapter.
    Keeping this boundary here prevents provider credentials from reaching Android.
    """

    async def process_chunk(self, session: AudioSession, data: bytes) -> None:
        # Intentionally no persistence of raw audio.
        return None


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
                data = message["bytes"]
                if len(data) > 256 * 1024:
                    await websocket.send_json({"type": "error", "code": "frame_too_large"})
                    continue
                await pipeline.process_chunk(session, data)
                await websocket.send_json({"type": "audio_ack", "bytes": len(data)})
            elif message.get("text"):
                await websocket.send_json({"type": "control_ack", "message": message["text"]})
    except WebSocketDisconnect:
        pass
