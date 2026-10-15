"""Low-latency inference routing for Saphira (Tier S latency pillar)."""

from .router import LatencyRouter, LatencyDecision

__all__ = ["LatencyRouter", "LatencyDecision"]
