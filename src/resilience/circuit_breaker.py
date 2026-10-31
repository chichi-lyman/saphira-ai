# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella

"""
Lightweight circuit breaker for LLM providers and external integrations.

States:
  CLOSED   — normal traffic
  OPEN     — fail fast after threshold consecutive failures
  HALF_OPEN — probe after recovery timeout
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import logging

logger = logging.getLogger("Saphira.CircuitBreaker")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when the circuit is open and the call is short-circuited."""

    def __init__(self, name: str, retry_after: float):
        self.name = name
        self.retry_after = retry_after
        super().__init__(f"Circuit '{name}' is OPEN; retry after {retry_after:.1f}s")


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 30.0  # seconds before half-open probe
    success_threshold: int = 2  # successes in half-open to close
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _opened_at: float = field(default=0.0, init=False)
    _last_error: Optional[str] = field(default=None, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._opened_at >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info("circuit %s -> HALF_OPEN (probe)", self.name)
        return self._state

    def allow(self) -> bool:
        """Return True if a call may proceed."""
        st = self.state
        if st == CircuitState.CLOSED:
            return True
        if st == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                self._last_error = None
                logger.info("circuit %s -> CLOSED (recovered)", self.name)
        else:
            self._failure_count = 0

    def record_failure(self, error: Optional[str] = None) -> None:
        self._last_error = error
        self._failure_count += 1
        if self.state == CircuitState.HALF_OPEN:
            self._trip()
            return
        if self._failure_count >= self.failure_threshold:
            self._trip()

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()
        self._success_count = 0
        logger.warning(
            "circuit %s OPEN after %d failures (last=%s)",
            self.name,
            self._failure_count,
            self._last_error,
        )

    def retry_after(self) -> float:
        if self.state != CircuitState.OPEN:
            return 0.0
        elapsed = time.monotonic() - self._opened_at
        return max(0.0, self.recovery_timeout - elapsed)

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "retry_after": round(self.retry_after(), 2),
            "last_error": self._last_error,
        }

    def reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at = 0.0
        self._last_error = None
