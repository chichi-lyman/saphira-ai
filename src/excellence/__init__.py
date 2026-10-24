"""Saphira competitive excellence pillars.

Design targets for latency, memory, automation, edge/offline, reasoning, and
privacy — owned by internal agents and exposed as registry capabilities.

Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""

from .pillars import EXCELLENCE_PILLARS, ExcellencePillar
from .agent_map import AGENT_EXCELLENCE_MAP, owners_for_pillar
from .router import ExcellenceRouter, route_excellence

__all__ = [
    "EXCELLENCE_PILLARS",
    "ExcellencePillar",
    "AGENT_EXCELLENCE_MAP",
    "owners_for_pillar",
    "ExcellenceRouter",
    "route_excellence",
]
