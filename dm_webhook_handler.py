"""
Flask-based webhook handler for Meta / Facebook Page DMs.

Verifies Meta connection (challenge) requests and can reply to incoming
Page DMs with sales or support links. Requires environment variables
for the verify token and page access token; never hardcode secrets.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Any, Dict, Optional

try:
    from flask import Flask, request, jsonify, Response
except ImportError:  # pragma: no cover - optional dependency for this module
    Flask = None  # type: ignore

logger = logging.getLogger("SaphiraDMWebhook")

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "")
PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
APP_SECRET = os.getenv("META_APP_SECRET", "")


def create_app() -> Any:
    if Flask is None:
        raise RuntimeError("Flask is required to run the Meta DM webhook handler.")

    app = Flask(__name__)

    @app.get("/webhook")
    def verify() -> Any:
        """Meta webhook verification (hub.challenge handshake)."""
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token and token == VERIFY_TOKEN:
            return Response(challenge or "", status=200, mimetype="text/plain")
        return jsonify({"error": "Verification failed"}), 403

    @app.post("/webhook")
    def receive() -> Any:
        """Receive Page messaging events. Signature check is best-effort when secret is set."""
        raw = request.get_data()
        if APP_SECRET:
            sig = request.headers.get("X-Hub-Signature-256", "")
            expected = "sha256=" + hmac.new(
                APP_SECRET.encode("utf-8"), raw, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig, expected):
                logger.warning("Invalid Meta webhook signature")
                return jsonify({"error": "Invalid signature"}), 403

        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        # Minimal safe handling: log and acknowledge. Business logic can be extended.
        logger.info("Meta webhook event received: object=%s", payload.get("object"))
        return jsonify({"status": "ok"}), 200

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "healthy", "service": "saphira-dm-webhook"}), 200

    return app


if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("PORT", "8080"))
    application.run(host="0.0.0.0", port=port)
