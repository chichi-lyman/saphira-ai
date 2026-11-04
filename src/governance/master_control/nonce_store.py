"""Nonce-store contract and development-only in-memory implementation.
Production deployments must replace this with an atomic, durable store (for example Redis SET NX with TTL)."""
from threading import Lock
class InMemoryNonceStore:
    def __init__(self): self._items=set(); self._lock=Lock()
    def consume(self,nonce,expires_at):
        with self._lock:
            if nonce in self._items: return False
            self._items.add(nonce); return True
