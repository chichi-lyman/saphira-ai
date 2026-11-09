# © 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella
"""Async Redis pub/sub bridge: Saphira edge ↔ Nova Umbrella control plane."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from pydantic import BaseModel, Field

try:
    import redis.asyncio as aioredis
except ImportError:  # pragma: no cover
    aioredis = None  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Saphira-Nova-Bridge) %(message)s",
)
logger = logging.getLogger("SaphiraNovaBridge")


class BridgeConfig:
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CHANNEL_EDGE_TO_NOVA: str = "nova:events:edge"
    CHANNEL_NOVA_TO_EDGE: str = "saphira:directives:inbound"
    CHANNEL_HEARTBEAT: str = "nova:telemetry:heartbeat"


class SaphiraEventPayload(BaseModel):
    source_node: str = Field(default="saphira-edge-termux")
    event_type: str
    session_id: str
    payload: Dict[str, Any]


class SaphiraNovaBridge:
    def __init__(self, config: Optional[BridgeConfig] = None):
        self.config = config or BridgeConfig()
        self.redis_client = None
        self.pubsub = None
        self.is_running = False

    async def connect(self) -> None:
        if aioredis is None:
            raise RuntimeError("redis package not installed (pip install redis)")
        logger.info(
            "Connecting to Nova bus at %s:%s...",
            self.config.REDIS_HOST,
            self.config.REDIS_PORT,
        )
        self.redis_client = aioredis.Redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            db=self.config.REDIS_DB,
            password=self.config.REDIS_PASSWORD,
            decode_responses=True,
        )
        await self.redis_client.ping()
        logger.info("Connected to Redis event bus.")

    async def publish_event(
        self, event_type: str, session_id: str, payload: Dict[str, Any]
    ) -> None:
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        message = SaphiraEventPayload(
            event_type=event_type, session_id=session_id, payload=payload
        ).model_dump_json()
        await self.redis_client.publish(self.config.CHANNEL_EDGE_TO_NOVA, message)
        logger.debug("Published %s session=%s", event_type, session_id)

    async def _heartbeat_loop(self) -> None:
        while self.is_running:
            try:
                hb = {
                    "node_id": "saphira-edge-termux",
                    "status": "ONLINE",
                    "runtime": "Termux-Linux-FastAPI",
                }
                if self.redis_client:
                    await self.redis_client.publish(
                        self.config.CHANNEL_HEARTBEAT, json.dumps(hb)
                    )
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Heartbeat error: %s", e)
                await asyncio.sleep(5)

    async def subscribe_directives(
        self, directive_handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(self.config.CHANNEL_NOVA_TO_EDGE)
        logger.info("Subscribed to %s", self.config.CHANNEL_NOVA_TO_EDGE)
        self.is_running = True
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        try:
            async for message in self.pubsub.listen():
                if message.get("type") == "message":
                    data = json.loads(message["data"])
                    logger.info(
                        "Directive: %s", data.get("action", "UNKNOWN")
                    )
                    asyncio.create_task(directive_handler(data))
        except asyncio.CancelledError:
            logger.info("Subscription shutting down...")
        finally:
            self.is_running = False
            heartbeat_task.cancel()

    async def disconnect(self) -> None:
        self.is_running = False
        if self.pubsub:
            await self.pubsub.unsubscribe(self.config.CHANNEL_NOVA_TO_EDGE)
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected from Nova event bus.")


async def handle_nova_directive(directive: Dict[str, Any]) -> None:
    action = directive.get("action")
    if action == "UPDATE_O_LORA_WEIGHTS":
        logger.info("O-LoRA update requested by orchestrator")
    elif action == "EXECUTE_SYMBOLIC_AST":
        logger.info("Symbolic AST execution requested")
    else:
        logger.warning("Unhandled directive: %s", action)


async def main() -> None:
    bridge = SaphiraNovaBridge()
    await bridge.connect()
    await bridge.publish_event(
        event_type="NODE_BOOTSTRAP",
        session_id="sys-init",
        payload={
            "status": "READY",
            "capabilities": ["O-LoRA", "SymbolicVerifier", "TermuxEdge"],
        },
    )
    try:
        await bridge.subscribe_directives(handle_nova_directive)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    finally:
        await bridge.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
