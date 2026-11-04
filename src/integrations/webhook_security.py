"""HMAC-SHA256 webhook authentication with timestamp and replay checks."""
from __future__ import annotations

import hashlib
import hmac
import time
from collections import OrderedDict


class WebhookSignatureVerifier:
    def __init__(self, secret: str, tolerance_seconds: int = 300, max_seen: int = 10000) -> None:
        if len(secret) < 32:
            raise ValueError("secret must contain at least 32 characters")
        self.secret = secret.encode()
        self.tolerance_seconds = tolerance_seconds
        self.max_seen = max_seen
        self.seen: OrderedDict[str, float] = OrderedDict()

    def signature(self, timestamp: int, raw_body: bytes) -> str:
        return hmac.new(self.secret, str(timestamp).encode() + b"." + raw_body,
                        hashlib.sha256).hexdigest()

    def verify(self, timestamp: int, raw_body: bytes, signature: str,
               event_id: str, now: float | None = None) -> bool:
        current = time.time() if now is None else now
        if not event_id or abs(current - timestamp) > self.tolerance_seconds:
            return False
        if not hmac.compare_digest(self.signature(timestamp, raw_body), signature):
            return False
        if event_id in self.seen:
            return False
        self.seen[event_id] = current
        while len(self.seen) > self.max_seen:
            self.seen.popitem(last=False)
        return True
