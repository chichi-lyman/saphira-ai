"""
src/tools/crawler/responsible_crawler.py
Focused + Incremental Responsible Crawler for Saphira AI
Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.

Hard rules:
- Always check robots.txt before any request.
- Rate-limit per host.
- Never attempt login, CAPTCHA, or authentication bypass.
- Return clean text only; never raw HTML to the LLM layer.
"""

from __future__ import annotations

import asyncio
import time
from typing import Optional
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

import httpx

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # type: ignore


class ResponsibleCrawler:
    def __init__(
        self,
        user_agent: str = "SaphiraAI-Research/1.1 (+https://github.com/chichi-lyman/saphira-ai)",
        default_delay: float = 2.5,
        max_pages_per_host: int = 5,
        request_timeout: float = 15.0,
    ):
        self.user_agent = user_agent
        self.default_delay = default_delay
        self.max_pages_per_host = max_pages_per_host
        self.request_timeout = request_timeout
        self._last_request: dict[str, float] = {}
        self._pages_fetched: dict[str, int] = {}
        self._robots_cache: dict[str, RobotFileParser] = {}

    def _host_key(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    async def _get_robots(self, url: str) -> RobotFileParser:
        host = self._host_key(url)
        if host not in self._robots_cache:
            rp = RobotFileParser()
            rp.set_url(urljoin(host, "/robots.txt"))
            try:
                await asyncio.to_thread(rp.read)
            except Exception:
                rp = RobotFileParser()
                rp.parse("User-agent: *\nDisallow: /")
            self._robots_cache[host] = rp
        return self._robots_cache[host]

    async def can_fetch(self, url: str) -> bool:
        rp = await self._get_robots(url)
        return rp.can_fetch(self.user_agent, url)

    async def _respect_rate_limit(self, host: str) -> None:
        now = time.monotonic()
        last = self._last_request.get(host, 0.0)
        wait = self.default_delay - (now - last)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request[host] = time.monotonic()

    def _check_host_budget(self, host: str) -> bool:
        count = self._pages_fetched.get(host, 0)
        return count < self.max_pages_per_host

    async def fetch_text(self, url: str, max_chars: int = 8000) -> dict:
        host = self._host_key(url)

        if not await self.can_fetch(url):
            return {"ok": False, "reason": "robots_disallowed", "url": url}

        if not self._check_host_budget(host):
            return {"ok": False, "reason": "host_budget_exceeded", "url": url}

        await self._respect_rate_limit(host)

        headers = {"User-Agent": self.user_agent, "Accept": "text/html,application/xhtml+xml"}
        try:
            async with httpx.AsyncClient(
                timeout=self.request_timeout,
                follow_redirects=True,
                headers=headers,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
        except Exception as exc:
            return {"ok": False, "reason": f"fetch_error:{type(exc).__name__}", "url": url}

        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return {"ok": False, "reason": "unsupported_content_type", "url": str(resp.url)}

        text = ""
        title = ""
        if BeautifulSoup is not None:
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "aside", "noscript"]):
                tag.decompose()
            title = (soup.title.string or "").strip()[:200] if soup.title else ""
            text = " ".join(soup.stripped_strings)[:max_chars]
        else:
            text = resp.text[:max_chars]

        self._pages_fetched[host] = self._pages_fetched.get(host, 0) + 1

        return {
            "ok": True,
            "url": str(resp.url),
            "title": title,
            "text": text,
            "status": resp.status_code,
            "fetched_at": time.time(),
        }

    async def refresh_page(self, url: str, max_chars: int = 8000) -> dict:
        return await self.fetch_text(url, max_chars=max_chars)
