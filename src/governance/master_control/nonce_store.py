"""Atomic nonce store contract. In-memory implementation is test-only."""
from threading import Lock
import time
class InMemoryNonceStore:
    def __init__(self,clock=time.time): self._items={}; self._lock=Lock(); self._clock=clock
    def consume(self,nonce,expires_at):
        now=int(self._clock())
        if not nonce or expires_at<=now: return False
        with self._lock:
            self._items={k:v for k,v in self._items.items() if v>now}
            if nonce in self._items: return False
            self._items[nonce]=expires_at
            return True
