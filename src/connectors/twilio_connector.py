# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Twilio communication gateway: SMS, voice, and multi-channel messaging.

Outbound calls and SMS are side-effecting. Callers must pass approved=True
after CommercialAuthorityPolicy / communications gates succeed. Credentials
never leave the server process.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

import httpx

logger = logging.getLogger("SaphiraTwilio")

TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"


class TwilioConnector:
    """Synchronous Twilio REST client used by the voice adapter and routers."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        status_callback_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.account_sid = (account_sid or os.getenv("TWILIO_ACCOUNT_SID", "")).strip()
        self.auth_token = (auth_token or os.getenv("TWILIO_AUTH_TOKEN", "")).strip()
        self.from_number = (from_number or os.getenv("TWILIO_FROM_NUMBER", "")).strip()
        self.status_callback_url = (
            status_callback_url or os.getenv("TWILIO_STATUS_CALLBACK_URL", "")
        ).strip()
        self.timeout = timeout

    def health(self) -> Dict[str, Any]:
        configured = bool(self.account_sid and self.auth_token and self.from_number)
        return {
            "status": "ready" if configured else "unconfigured",
            "provider": "twilio",
            "from_number_set": bool(self.from_number),
            "status_callback_set": bool(self.status_callback_url),
        }

    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.from_number)

    def send_sms(
        self,
        to: str,
        body: str,
        *,
        approved: bool = False,
    ) -> Dict[str, Any]:
        if not approved:
            return {
                "status": "denied",
                "message": "SMS requires policy approval (approved=True)",
                "capability": "communications.sms",
            }
        if not self.is_configured():
            return {"status": "error", "message": "Twilio credentials missing"}
        if not to or not body.strip():
            return {"status": "error", "message": "to and body are required"}

        data = {
            "To": to,
            "From": self.from_number,
            "Body": body[:1600],
        }
        return self._post_form(f"Accounts/{self.account_sid}/Messages.json", data)

    def start_voice_call(
        self,
        to: str,
        *,
        twiml_url: Optional[str] = None,
        say_text: Optional[str] = None,
        voice: str = "alice",
        language: str = "en-US",
        status_callback: Optional[str] = None,
        timeout_seconds: int = 30,
        approved: bool = False,
    ) -> Dict[str, Any]:
        """Place an outbound call.

        Provide either ``twiml_url`` (hosted TwiML) or ``say_text`` (inline TwiML
        via Twilio's Twiml parameter). Outbound calls require approved=True.
        """
        if not approved:
            return {
                "status": "denied",
                "message": "Outbound voice calls require policy approval (approved=True)",
                "capability": "communications.voice",
            }
        if not self.is_configured():
            return {"status": "error", "message": "Twilio credentials missing"}
        if not to:
            return {"status": "error", "message": "to is required"}
        if not twiml_url and not say_text:
            return {
                "status": "error",
                "message": "Provide twiml_url or say_text for the call flow",
            }

        data: Dict[str, Any] = {
            "To": to,
            "From": self.from_number,
            "Timeout": str(max(5, min(timeout_seconds, 600))),
        }
        if twiml_url:
            data["Url"] = twiml_url
            data["Method"] = "POST"
        else:
            data["Twiml"] = self.build_say_twiml(say_text or "", voice=voice, language=language)

        callback = status_callback or self.status_callback_url
        if callback:
            data["StatusCallback"] = callback
            data["StatusCallbackEvent"] = "initiated ringing answered completed"
            data["StatusCallbackMethod"] = "POST"

        result = self._post_form(f"Accounts/{self.account_sid}/Calls.json", data)
        if result.get("status") == "ok":
            payload = result.get("data") or {}
            result["call_sid"] = payload.get("sid")
            result["call_status"] = payload.get("status")
        return result

    def get_call(self, call_sid: str) -> Dict[str, Any]:
        if not self.account_sid or not self.auth_token:
            return {"status": "error", "message": "Twilio credentials missing"}
        if not call_sid:
            return {"status": "error", "message": "call_sid is required"}
        return self._get(f"Accounts/{self.account_sid}/Calls/{call_sid}.json")

    def hangup_call(self, call_sid: str, *, approved: bool = False) -> Dict[str, Any]:
        if not approved:
            return {
                "status": "denied",
                "message": "Hangup requires policy approval (approved=True)",
            }
        if not self.account_sid or not self.auth_token:
            return {"status": "error", "message": "Twilio credentials missing"}
        if not call_sid:
            return {"status": "error", "message": "call_sid is required"}
        return self._post_form(
            f"Accounts/{self.account_sid}/Calls/{call_sid}.json",
            {"Status": "completed"},
        )

    @staticmethod
    def build_say_twiml(
        text: str,
        *,
        voice: str = "alice",
        language: str = "en-US",
        hangup: bool = True,
    ) -> str:
        """Build minimal TwiML that speaks ``text`` then optionally hangs up."""
        safe = escape(text.strip() or "Hello from Saphira AI.")
        voice_attr = escape(voice)
        lang_attr = escape(language)
        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<Response>",
            f'<Say voice="{voice_attr}" language="{lang_attr}">{safe}</Say>',
        ]
        if hangup:
            parts.append("<Hangup/>")
        parts.append("</Response>")
        return "".join(parts)

    @staticmethod
    def build_gather_twiml(
        prompt: str,
        *,
        action_url: str,
        num_digits: int = 1,
        timeout: int = 5,
        voice: str = "alice",
        language: str = "en-US",
    ) -> str:
        """Build TwiML that prompts and gathers DTMF digits."""
        safe_prompt = escape(prompt.strip() or "Please enter a digit.")
        action = escape(action_url)
        voice_attr = escape(voice)
        lang_attr = escape(language)
        n = max(1, min(int(num_digits), 32))
        t = max(1, min(int(timeout), 30))
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Response>"
            f'<Gather numDigits="{n}" timeout="{t}" action="{action}" method="POST">'
            f'<Say voice="{voice_attr}" language="{lang_attr}">{safe_prompt}</Say>'
            "</Gather>"
            f'<Say voice="{voice_attr}" language="{lang_attr}">We did not receive input. Goodbye.</Say>'
            "<Hangup/>"
            "</Response>"
        )

    def _auth(self) -> tuple[str, str]:
        return (self.account_sid, self.auth_token)

    def _post_form(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{TWILIO_API_BASE}/{path.lstrip('/')}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, data=data, auth=self._auth())
            return self._normalize_response(resp)
        except httpx.TimeoutException:
            logger.error("Twilio timeout on POST %s", path)
            return {"status": "error", "message": "Twilio request timed out"}
        except Exception as exc:
            logger.exception("Twilio POST failed: %s", path)
            return {"status": "error", "message": str(exc)}

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{TWILIO_API_BASE}/{path.lstrip('/')}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, auth=self._auth())
            return self._normalize_response(resp)
        except httpx.TimeoutException:
            return {"status": "error", "message": "Twilio request timed out"}
        except Exception as exc:
            logger.exception("Twilio GET failed: %s", path)
            return {"status": "error", "message": str(exc)}

    @staticmethod
    def _normalize_response(resp: httpx.Response) -> Dict[str, Any]:
        try:
            payload = resp.json()
        except Exception:
            payload = {"raw": resp.text[:500]}

        if resp.status_code in (200, 201):
            return {"status": "ok", "http_status": resp.status_code, "data": payload}

        message = (
            payload.get("message")
            if isinstance(payload, dict)
            else None
        ) or resp.text[:300]
        logger.error("Twilio API error %s: %s", resp.status_code, message)
        return {
            "status": "error",
            "http_status": resp.status_code,
            "message": message,
            "data": payload if isinstance(payload, dict) else {},
        }


def twilio_connector_from_env() -> TwilioConnector:
    return TwilioConnector()
