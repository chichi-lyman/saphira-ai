# Wearable Data Connector (Heart Rate / HRV)
# Copyright © 2026 Chelsea Megan Woods
#
# Supports:
# - Mock / simulated data (for testing & offline)
# - Flutter platform channel bridge (Android Health Connect / iOS HealthKit)
# - Placeholder paths for Fitbit, Oura, Apple Health REST
# - Age of data freshness checks (stale after 5 minutes)

from typing import Dict, Any, Optional
import logging
import random
import time
from datetime import datetime, timezone

logger = logging.getLogger("SaphiraWearable")


class WearableConnector:
    """
    Abstraction layer for real-time heart-rate and HRV data.
    In production this talks to Health Connect / HealthKit via a Flutter
    platform channel or a local BLE / HTTP bridge.
    """

    _instance: Optional["WearableConnector"] = None

    def __new__(cls, source: str = "mock"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, source: str = "mock"):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.source = source
        self.channel_connected: bool = False
        self._latest_payload: Optional[Dict[str, Any]] = None
        self._last_reading: Optional[Dict[str, Any]] = None

    def receive_platform_channel_payload(self, payload: Dict[str, Any]) -> None:
        """
        Called by the Flutter / native side when new Health Connect / HealthKit
        data arrives. Keeps the most recent reading for the Python agents.
        """
        ts = payload.get("timestamp")
        if isinstance(ts, (int, float)):
            # already epoch seconds
            pass
        else:
            ts = time.time()

        self._latest_payload = {
            "hrv": float(payload.get("hrv", 55.0)),
            "resting_hr": float(payload.get("resting_hr", 68.0)),
            "sleep_score": float(payload.get("sleep_score", 80.0)),
            "timestamp": ts,
            "source": payload.get("source", "health_connect"),
        }
        self.channel_connected = True
        self._last_reading = self._latest_payload
        logger.info(
            "Platform channel biometrics received: HRV=%.1f HR=%.0f Sleep=%.0f",
            self._latest_payload["hrv"],
            self._latest_payload["resting_hr"],
            self._latest_payload["sleep_score"],
        )

    async def fetch_latest(self) -> Dict[str, Any]:
        """Return the most recent biometric snapshot (live preferred)."""
        return self.fetch_live_biometrics()

    def fetch_live_biometrics(self) -> Dict[str, Any]:
        """
        Synchronous helper used by agents and the live orchestrator.
        Prefers a fresh platform-channel payload; falls back to mock.
        """
        if (
            self._latest_payload
            and (time.time() - float(self._latest_payload["timestamp"]) < 300)
        ):
            return dict(self._latest_payload)

        if self.source == "health_connect" and self.channel_connected:
            # Stale – still return last known rather than pure mock
            if self._latest_payload:
                stale = dict(self._latest_payload)
                stale["source"] = f"{stale.get('source', 'health_connect')}_stale"
                return stale

        return self._generate_mock_reading()

    def _generate_mock_reading(self) -> Dict[str, Any]:
        """Realistic simulated values for development and tests."""
        reading = {
            "hrv": round(random.uniform(30.0, 90.0), 1),
            "resting_hr": float(random.randint(55, 95)),
            "sleep_score": float(random.randint(40, 95)),
            "timestamp": time.time(),
            "source": "mock",
        }
        self._last_reading = reading
        return reading

    def get_last_reading(self) -> Optional[Dict[str, Any]]:
        return self._last_reading

    def set_source(self, source: str) -> None:
        self.source = source


# Convenience singleton for quick access from agents & orchestrators
wearable = WearableConnector(source="mock")
wearable_connector = wearable  # alias used by live orchestrator
