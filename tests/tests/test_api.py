"""
© 2026 Chelsea Megan Woods. All rights reserved.
Saphira AI - FastAPI Endpoint Test Suite
Purpose: Validates live HTTP request handling across Saphira's routes.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["architect"] == "Chelsea Megan Woods"
    assert data["system"] == "Saphira AI Active"

@pytest.mark.asyncio
async def test_printer_status_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/iot/printer/status")
    assert response.status_code == 200
    data = response.json()
    assert data["print_state"] == "printing"
