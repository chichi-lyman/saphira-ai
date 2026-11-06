"""
src/tools/search/web_search.py
Search API adapter for Saphira AI
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

Prefers commercial search APIs over open crawling.
Supports Serper, Brave, or Bing via environment variables.
Returns only title / link / snippet — never full page content.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx


async def web_search(
    query: str,
    num_results: int = 8,
    *,
    provider: Optional[str] = None,
) -> list[dict[str, Any]]:
    provider = (provider or os.getenv("SAPHIRA_SEARCH_PROVIDER", "serper")).lower()
    num_results = max(1, min(num_results, 15))

    if provider == "serper":
        return await _serper_search(query, num_results)
    if provider == "brave":
        return await _brave_search(query, num_results)
    if provider == "bing":
        return await _bing_search(query, num_results)

    return [{"title": "", "link": "", "snippet": "", "error": f"unknown_provider:{provider}"}]


async def _serper_search(query: str, num: int) -> list[dict]:
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [{"error": "SERPER_API_KEY not set"}]

    async with httpx.AsyncClient(timeout=12.0) as client:
        resp = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num},
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("organic", [])[:num]:
        results.append({
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        })
    return results


async def _brave_search(query: str, num: int) -> list[dict]:
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        return [{"error": "BRAVE_SEARCH_API_KEY not set"}]

    async with httpx.AsyncClient(timeout=12.0) as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
            params={"q": query, "count": num},
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("web", {}).get("results", [])[:num]:
        results.append({
            "title": item.get("title", ""),
            "link": item.get("url", ""),
            "snippet": item.get("description", ""),
        })
    return results


async def _bing_search(query: str, num: int) -> list[dict]:
    api_key = os.getenv("BING_SEARCH_API_KEY")
    if not api_key:
        return [{"error": "BING_SEARCH_API_KEY not set"}]

    async with httpx.AsyncClient(timeout=12.0) as client:
        resp = await client.get(
            "https://api.bing.microsoft.com/v7.0/search",
            headers={"Ocp-Apim-Subscription-Key": api_key},
            params={"q": query, "count": num},
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("webPages", {}).get("value", [])[:num]:
        results.append({
            "title": item.get("name", ""),
            "link": item.get("url", ""),
            "snippet": item.get("snippet", ""),
        })
    return results
