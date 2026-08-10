from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class AsymmetricA2AMessage(BaseModel):
    sender_did: str
    recipient_did: str
    tenant_id: str
    nonce: str
    timestamp: float
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    signature_hex: str


def canonical_payload(message: AsymmetricA2AMessage | dict[str, Any]) -> bytes:
    if isinstance(message, AsymmetricA2AMessage):
        data = message.model_dump(exclude={"signature_hex"})
    else:
        data = message
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


class AsymmetricA2AMesh:
    def __init__(self, public_key_registry: dict[str, bytes]):
        self.public_key_registry = public_key_registry

    @staticmethod
    def generate_agent_keypair() -> tuple[bytes, bytes]:
        private = ed25519.Ed25519PrivateKey.generate()
        public = private.public_key()
        return (
            private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()),
            public.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw),
        )

    @staticmethod
    def sign_message(private_key_bytes: bytes, message: dict[str, Any]) -> str:
        private = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        return private.sign(canonical_payload(message)).hex()

    def verify_message(self, message: AsymmetricA2AMessage, max_clock_skew_seconds: float = 30.0) -> bool:
        if abs(time.time() - message.timestamp) > max_clock_skew_seconds:
            raise ValueError("A2A message timestamp expired or clock skew is too high")
        pub_bytes = self.public_key_registry.get(message.sender_did)
        if not pub_bytes:
            raise PermissionError("Unrecognized agent public key")
        try:
            signature = bytes.fromhex(message.signature_hex)
            ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes).verify(signature, canonical_payload(message))
        except (ValueError, TypeError) as exc:
            raise PermissionError("Invalid A2A signature encoding") from exc
        except Exception as exc:
            raise PermissionError("Cryptographic signature invalid") from exc
        return True
