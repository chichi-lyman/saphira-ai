"""
© 2026 Chelsea Megan Woods. All rights reserved.
Saphira AI - Core Router Test Suite
Purpose: Tests natural language parsing and intent routing for IoT and entertainment controllers.
"""

import pytest
from saphira.core.router import SaphiraRouter

@pytest.fixture
def router():
    return SaphiraRouter()

@pytest.mark.asyncio
async def test_router_lighting_intent(router):
    result = await router.process_intent("turn off the living room light")
    assert result["status"] == "success"
    assert "off" in str(result).lower() or "light" in str(result).lower()

@pytest.mark.asyncio
async def test_router_printer_intent(router):
    result = await router.process_intent("check the 3D printer status")
    assert result["status"] == "success"
    assert result["device_id"] == "corexy_printer_1"

@pytest.mark.asyncio
async def test_router_media_intent(router):
    result = await router.process_intent("change channel to sports news")
    assert result["status"] == "success"
