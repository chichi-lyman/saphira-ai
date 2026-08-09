"""Runtime event bus for quiet background execution and live UI updates."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from .task import TaskEvent

Subscriber = Callable[[TaskEvent], Awaitable[None] | None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []
        self._queue: asyncio.Queue[TaskEvent] = asyncio.Queue()

    def subscribe(self, subscriber: Subscriber) -> None:
        self._subscribers.append(subscriber)

    async def publish(self, event: TaskEvent) -> None:
        await self._queue.put(event)
        for subscriber in tuple(self._subscribers):
            result = subscriber(event)
            if result is not None:
                await result

    async def next(self) -> TaskEvent:
        return await self._queue.get()

    async def stream(self):
        while True:
            yield await self.next()
