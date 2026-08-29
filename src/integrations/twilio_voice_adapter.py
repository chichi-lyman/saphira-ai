# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Async PluginAdapter for Twilio voice / SMS capabilities.

Registers against the integrations PluginRegistry. Side-effecting capabilities
require ``approved=True`` in arguments after policy gates pass.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from src.connectors.twilio_connector import TwilioConnector, twilio_connector_from_env

logger = logging.getLogger("SaphiraTwilioVoiceAdapter")

VOICE_CAPABILITIES = frozenset(
    {
        "voice.call",
        "voice.status",
        "voice.hangup",
        "voice.twiml.say",
        "voice.twiml.gather",
        "sms.send",
        "health",
    }
)


class TwilioVoiceAdapter:
    """PluginAdapter-compatible Twilio voice surface."""

    name = "twilio"
    version = "1.0"

    def __init__(self, connector: TwilioConnector | None = None) -> None:
        self._connector = connector or twilio_connector_from_env()

    async def health(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self._connector.health)

    async def invoke(self, capability: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        cap = (capability or "").strip().lower()
        args = arguments or {}

        if cap not in VOICE_CAPABILITIES and cap not in {
            "communications",
            "sms",
            "voice",
            "messaging",
        }:
            return {
                "status": "error",
                "message": f"Unsupported Twilio capability: {capability}",
                "supported": sorted(VOICE_CAPABILITIES),
            }

        try:
            if cap in {"health"}:
                return await self.health()

            if cap in {"voice.call", "voice", "communications"}:
                return await self._call(args)

            if cap in {"voice.status"}:
                return await asyncio.to_thread(
                    self._connector.get_call, str(args.get("call_sid", ""))
                )

            if cap in {"voice.hangup"}:
                return await asyncio.to_thread(
                    self._connector.hangup_call,
                    str(args.get("call_sid", "")),
                    approved=bool(args.get("approved", False)),
                )

            if cap in {"voice.twiml.say"}:
                twiml = self._connector.build_say_twiml(
                    str(args.get("text", "")),
                    voice=str(args.get("voice", "alice")),
                    language=str(args.get("language", "en-US")),
                    hangup=bool(args.get("hangup", True)),
                )
                return {"status": "ok", "twiml": twiml}

            if cap in {"voice.twiml.gather"}:
                action_url = str(args.get("action_url", "")).strip()
                if not action_url:
                    return {"status": "error", "message": "action_url is required"}
                twiml = self._connector.build_gather_twiml(
                    str(args.get("prompt", "")),
                    action_url=action_url,
                    num_digits=int(args.get("num_digits", 1)),
                    timeout=int(args.get("timeout", 5)),
                    voice=str(args.get("voice", "alice")),
                    language=str(args.get("language", "en-US")),
                )
                return {"status": "ok", "twiml": twiml}

            if cap in {"sms.send", "sms", "messaging"}:
                return await asyncio.to_thread(
                    self._connector.send_sms,
                    str(args.get("to", "")),
                    str(args.get("body", "")),
                    approved=bool(args.get("approved", False)),
                )

            return {"status": "error", "message": f"Unhandled capability: {capability}"}
        except Exception as exc:
            logger.exception("TwilioVoiceAdapter invoke failed: %s", capability)
            return {"status": "error", "message": str(exc), "recovered_from_failure": True}

    async def _call(self, args: Dict[str, Any]) -> Dict[str, Any]:
        to = str(args.get("to", "")).strip()
        say_text = args.get("say_text") or args.get("text")
        twiml_url = args.get("twiml_url") or args.get("url")
        return await asyncio.to_thread(
            self._connector.start_voice_call,
            to,
            twiml_url=str(twiml_url) if twiml_url else None,
            say_text=str(say_text) if say_text else None,
            voice=str(args.get("voice", "alice")),
            language=str(args.get("language", "en-US")),
            status_callback=str(args.get("status_callback")) if args.get("status_callback") else None,
            timeout_seconds=int(args.get("timeout_seconds", 30)),
            approved=bool(args.get("approved", False)),
        )


def register_twilio_voice(registry: Any) -> TwilioVoiceAdapter:
    """Register Twilio voice adapter on an integrations PluginRegistry instance."""
    from src.integrations.plugin_registry import PluginManifest

    adapter = TwilioVoiceAdapter()
    manifest = PluginManifest(
        name="twilio",
        version="1.0",
        description="Voice-to-text calls, SMS alerts, and multi-channel messaging gateway",
        capabilities=("communications", "sms", "voice", "messaging"),
        scopes=("send", "call"),
        requires_approval=True,
        side_effects=True,
        enabled=adapter._connector.is_configured(),
        metadata={"category": "extended_workflow", "adapter": "TwilioVoiceAdapter"},
    )
    registry.register(manifest, adapter)
    return adapter
