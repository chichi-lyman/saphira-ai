"""Offline intent queue when cloud models are unavailable."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class QueuedIntent:
    id: str
    tenant_id: str
    user_id: str
    text: str
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class OfflineQueue:
    def __init__(self) -> None:
        self._items: List[QueuedIntent] = []
        self.cloud_available: bool = True
    def enqueue(self, tenant_id: str, user_id: str, text: str, **meta: Any) -> QueuedIntent:
        item = QueuedIntent(id=str(uuid.uuid4()), tenant_id=tenant_id, user_id=user_id, text=text, metadata=dict(meta))
        self._items.append(item)
        return item
    def drain(self) -> List[QueuedIntent]:
        items = list(self._items)
        self._items.clear()
        return items
    def pending_count(self) -> int:
        return len(self._items)

offline_queue = OfflineQueue()
