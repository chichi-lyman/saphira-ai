# Wearable Data Connector (Heart Rate / HRV)
# Copyright © 2026 Chelsea Megan Woods
#
# Supports:
# - Mock / simulated data (for testing)
# - Health Connect / Google Fit style APIs
# - Simple REST endpoints from common wearables

from typing import Dict, Any, Optional
import logging
import random
from datetime import datetime, timezone

logger = logging.getLogger("SaphiraWearable")


class WearableConnector:
    """
    Abstraction layer for real-time heart-rate and HRV data.
    In production this would talk to Health Connect, Fitbit, Oura, or a local BLE bridge.
    """

    def __init__(self, source: str = "mock"):
        self.source = source
        self._last_reading: Optional[Dict[str, Any]] = None

    async def fetch_latest(self) -> Dict[str, Any]:
        """Return the most recent biometric snapshot."""
        if self.source == "mock":
            return self._generate_mock_reading()
        elif self.source == "health_connect":
            return await self._fetch_health_connect()
        else:
            logger.warning(f"Unknown wearable source: {self.source}. Falling back to mock.")
            return self._generate_mock_reading()

    def _generate_mock_reading(self) -> Dict[str, Any]:
        """Realistic simulated values for development and tests."""
        reading = {
            "hrv": round(random.uniform(30, 90), 1),
            "resting_hr": random.randint(55, 95),
            "sleep_score": random.randint(40, 95),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "mock"
        }
        self._last_reading = reading
        return reading

    async def _fetch_health_connect(self) -> Dict[str, Any]:
        """
        Placeholder for real Health Connect / Google Fit integration.
        In a production Android build this would call the native Health Connect SDK
        via a Flutter/Platform channel or a local HTTP bridge.
        """
        # Example structure that a real bridge would return
        logger.info("Health Connect bridge not yet connected – returning mock data")
        return self._generate_mock_reading()

    def get_last_reading(self) -> Optional[Dict[str, Any]]:
        return self._last_reading


# Convenience singleton for quick access from agents
wearable = WearableConnector(source="mock")
