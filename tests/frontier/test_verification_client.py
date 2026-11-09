# © 2026 Chelsea Megan Woods · Nova Umbrella
"""Smoke client for REST + WebSocket formal verification endpoints."""
from __future__ import annotations

import asyncio
import json
import os

import requests

SERVER_URL = os.environ.get("SAPHIRA_VERIFY_URL", "http://127.0.0.1:8000")
WS_URL = os.environ.get("SAPHIRA_VERIFY_WS", "ws://127.0.0.1:8000/ws/verify")

PAYLOAD = {
    "session_id": "nova-agent-77",
    "sympy_spec": {
        "expr1": "cos(x)**2 + sin(x)**2",
        "expr2": "1",
    },
    "z3_spec": {
        "variables": ["temperature"],
        "constraints": ["temperature >= 20", "temperature <= 100"],
        "assertion": "temperature * 1.8 + 32 >= 68",
    },
    "code_payload": "result = sum([x for x in range(10)])",
}


def test_rest() -> None:
    print("--- REST /v1/verify/formal ---")
    r = requests.post(f"{SERVER_URL}/v1/verify/formal", json=PAYLOAD, timeout=30)
    print(json.dumps(r.json(), indent=2))


async def test_ws() -> None:
    try:
        import websockets
    except ImportError:
        print("websockets not installed — skip WS test")
        return
    print("--- WebSocket /ws/verify ---")
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps(PAYLOAD))
        response = await ws.recv()
        print(json.dumps(json.loads(response), indent=2))


if __name__ == "__main__":
    try:
        test_rest()
    except Exception as e:
        print("REST failed (is server up?):", e)
    try:
        asyncio.run(test_ws())
    except Exception as e:
        print("WS failed:", e)
