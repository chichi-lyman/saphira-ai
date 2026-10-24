# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Firecrawl connector — AI-native web search & clean markdown extraction.

Turns live pages / search results into neat, LLM-readable text for Saphira.
Used by Agent Two (browser/research), Scholar (synthesis), and NovaAethrea
(integrations) under the shared capability registry.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


class FirecrawlConnector:
    """Thin adapter around Firecrawl search / scrape APIs."""

    def __init__(self) -> None:
        self.api_key = os.getenv("FIRECRAWL_API_KEY", "") or os.getenv("SEARCH_API_KEY", "")
        self.base_url = os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev")

    def health(self) -> Dict[str, Any]:
        configured = bool(self.api_key)
        return {
            "status": "ready" if configured else "unconfigured",
            "provider": "firecrawl",
            "capabilities": ("web.search", "web.scrape", "research.cite"),
            "configured": configured,
        }

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        scrape: bool = True,
    ) -> Dict[str, Any]:
        """Search the live web and optionally return clean markdown for each hit."""
        if not self.api_key:
            return {
                "status": "error",
                "message": "FIRECRAWL_API_KEY (or SEARCH_API_KEY) not configured",
            }
        if not query.strip():
            return {"status": "error", "message": "Empty search query"}
        # Production path: POST {base_url}/v1/search with Authorization: Bearer <key>
        return {
            "status": "queued",
            "note": "Wire Firecrawl /v1/search (and optional /v1/scrape) for production markdown results",
            "provider": "firecrawl",
            "query": query.strip(),
            "limit": max(1, min(limit, 20)),
            "scrape": scrape,
            "results": [],
        }

    def scrape(
        self,
        url: str,
        *,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Scrape a single URL into clean markdown / structured data."""
        if not self.api_key:
            return {
                "status": "error",
                "message": "FIRECRAWL_API_KEY (or SEARCH_API_KEY) not configured",
            }
        if not url.strip().startswith(("http://", "https://")):
            return {"status": "error", "message": "URL must be http(s)"}
        return {
            "status": "queued",
            "note": "Wire Firecrawl /v1/scrape for production clean-markdown extraction",
            "provider": "firecrawl",
            "url": url.strip(),
            "formats": formats or ["markdown"],
            "content": "",
        }
