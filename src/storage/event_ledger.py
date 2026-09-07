# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""Append-only JSONL event ledger for worker telemetry."""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SaphiraEventLedger:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or os.getenv("SAPHIRA_EVENT_LEDGER_PATH", "storage/logs/sentinel_event_ledger.jsonl"))

    async def commit_log(self, *, layer: str, node: str, tenant_id: str, status: str, payload: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "layer": layer,
            "node": node,
            "tenant_id": tenant_id,
            "status": status,
            "payload": payload,
        }
        await asyncio.to_thread(self._append, record)

    def _append(self, record: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str, separators=(",", ":")) + "\n")
