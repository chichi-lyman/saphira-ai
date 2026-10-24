# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""Tavily connector — AI-native search layer optimized for agents.

Provides real-time web search with clean, citation-ready snippets for Saphira's
web_grounding and research.cite capabilities.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional


class TavilyConnector:
    """Adapter for Tavily Search API."""

    def __init__(self) -> None:
        self.api_key = os.getenv("TAVILY_API_KEY", "") or os.getenv("SEARCH_API_KEY", "")
        self.base_url = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com")

    def health(self) -> Dict[str, Any]:
        configured = bool(self.api_key)
        return {
            "status": "ready" if configured else "unconfigured",
            "provider": "tavily",
            "capabilities": ("web.search", "research.cite", "research.factcheck"),
            "configured": configured,
        }

    def search(
        self,
        query: str,
        *,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = True,
    ) -> Dict[str, Any]:
        """Run a Tavily search and return structured, citation-friendly results."""
        if not self.api_key:
            return {
                "status": "error",
                "message": "TAVILY_API_KEY (or SEARCH_API_KEY) not configured",
            }
        if not query.strip():
            return {"status": "error", "message": "Empty search query"}
        depth = search_depth if search_depth in {"basic", "advanced"} else "basic"
        return {
            "status": "queued",
            "note": "Wire Tavily /search endpoint for production results with answer + sources",
            "provider": "tavily",
            "query": query.strip(),
            "max_results": max(1, min(max_results, 20)),
            "search_depth": depth,
            "include_answer": include_answer,
            "results": [],
            "answer": None,
        }
