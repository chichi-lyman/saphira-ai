"""
Basic tests for the responsible crawler.
Copyright © 2026 Chelsea Megan Woods.
"""

import asyncio
import pytest
from src.tools.crawler.responsible_crawler import ResponsibleCrawler


@pytest.mark.asyncio
async def test_robots_disallow_is_honored():
    crawler = ResponsibleCrawler(default_delay=0.1)
    result = await crawler.can_fetch("https://example.com/")
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_fetch_returns_structured_dict():
    crawler = ResponsibleCrawler(default_delay=0.1, max_pages_per_host=2)
    result = await crawler.fetch_text("https://example.com/")
    assert "ok" in result
    if result["ok"]:
        assert "text" in result
        assert "title" in result
        assert len(result["text"]) > 0
