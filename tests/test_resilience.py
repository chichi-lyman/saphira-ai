# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Unit tests for circuit breaker + graceful degradation (no live API calls).

import time
import pytest

from src.resilience.circuit_breaker import CircuitBreaker, CircuitState, CircuitOpenError
from src.resilience.degradation import GracefulDegradation, DegradationLevel


def test_circuit_starts_closed():
    cb = CircuitBreaker(name="test", failure_threshold=3, recovery_timeout=0.2)
    assert cb.state == CircuitState.CLOSED
    assert cb.allow() is True


def test_circuit_opens_after_threshold():
    cb = CircuitBreaker(name="test", failure_threshold=3, recovery_timeout=10.0)
    for _ in range(3):
        cb.record_failure("boom")
    assert cb.state == CircuitState.OPEN
    assert cb.allow() is False


def test_circuit_half_open_and_recover():
    cb = CircuitBreaker(
        name="test", failure_threshold=2, recovery_timeout=0.05, success_threshold=2
    )
    cb.record_failure("a")
    cb.record_failure("b")
    assert cb.state == CircuitState.OPEN
    time.sleep(0.06)
    assert cb.state == CircuitState.HALF_OPEN
    assert cb.allow() is True
    cb.record_success()
    cb.record_success()
    assert cb.state == CircuitState.CLOSED


def test_circuit_half_open_fails_trips_again():
    cb = CircuitBreaker(
        name="test", failure_threshold=2, recovery_timeout=0.05, success_threshold=2
    )
    cb.record_failure("a")
    cb.record_failure("b")
    time.sleep(0.06)
    assert cb.state == CircuitState.HALF_OPEN
    cb.record_failure("still down")
    assert cb.state == CircuitState.OPEN


def test_degradation_full_to_standby():
    g = GracefulDegradation()
    health = {
        "providers": {
            "gemini": {"enabled": True, "circuit": {"state": "closed"}},
            "openai": {"enabled": True, "circuit": {"state": "closed"}},
        }
    }
    assert g.update_from_provider_health(health) == DegradationLevel.FULL

    health["providers"]["gemini"]["circuit"]["state"] = "open"
    assert g.update_from_provider_health(health) == DegradationLevel.REDUCED

    health["providers"]["openai"]["circuit"]["state"] = "open"
    assert g.update_from_provider_health(health) == DegradationLevel.STANDBY

    msg = g.standby_message("timeout")
    assert "Standby" in msg
    assert "timeout" in msg
