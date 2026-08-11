"""Zero-cost public business lead discovery primitives.

This module intentionally uses Python's standard library only. It provides a
source-adapter-friendly discovery pipeline and a deterministic HTML parser for
fixtures/tests. It does not bypass access controls, CAPTCHAs, authentication,
or source restrictions.
"""
from __future__ import annotations

import csv
import hashlib
import html
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urljoin, urlparse
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Lead:
    business_name: str
    website: str = ""
    business_phone: str = ""
    city: str = ""
    state: str = ""
    industry: str = ""
    source_url: str = ""
    source_name: str = ""
    discovered_at: str = ""


class _BusinessHTMLParser(HTMLParser):
    """Small fixture-oriented parser for clearly marked business cards."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._field: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if "business-card" in classes:
            self._current = {}
        if self._current is not None:
            if "business-name" in classes:
                self._field = "business_name"
            elif "business-phone" in classes:
                self._field = "business_phone"
            elif "business-website" in classes:
                href = attributes.get("href") or ""
                self._current["website"] = href
                self._field = None

    def handle_endtag(self, tag: str) -> None:
        if self._current is not None and self._field:
            self._field = None
        if self._current is not None and tag == "article":
            if self._current.get("business_name"):
                self.records.append(self._current)
            self._current = None

    def handle_data(self, data: str) -> None:
        if self._current is not None and self._field:
            value = " ".join(data.split())
            if value:
                self._current[self._field] = (self._current.get(self._field, "") + " " + value).strip()


def _clean_phone(value: str) -> str:
    value = re.sub(r"\s+", " ", html.unescape(value)).strip()
    return value


def _normalize_url(value: str, base_url: str = "") -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("//"):
        value = "https:" + value
    elif base_url and not urlparse(value).scheme:
        value = urljoin(base_url, value)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return value.split("#", 1)[0]


def normalize_leads(records: Iterable[Lead]) -> list[Lead]:
    """Normalize and deduplicate business records by website/name+location."""
    result: list[Lead] = []
    seen: set[str] = set()
    for lead in records:
        name = " ".join(lead.business_name.split()).strip()
        website = _normalize_url(lead.website)
        key_source = website.lower() or f"{name.lower()}|{lead.city.lower()}|{lead.state.lower()}"
        key = hashlib.sha256(key_source.encode("utf-8")).hexdigest()
        if not name or key in seen:
            continue
        seen.add(key)
        result.append(
            Lead(
                business_name=name,
                website=website,
                business_phone=_clean_phone(lead.business_phone),
                city=lead.city.strip(),
                state=lead.state.strip(),
                industry=lead.industry.strip(),
                source_url=lead.source_url.strip(),
                source_name=lead.source_name.strip(),
                discovered_at=lead.discovered_at or datetime.now(timezone.utc).isoformat(),
            )
        )
    return result


def parse_fixture_html(html_text: str, *, source_url: str, source_name: str,
                       industry: str, city: str = "", state: str = "") -> list[Lead]:
    """Parse deterministic business-card fixtures without network access."""
    parser = _BusinessHTMLParser()
    parser.feed(html_text)
    return normalize_leads(
        Lead(
            business_name=item.get("business_name", ""),
            website=item.get("website", ""),
            business_phone=item.get("business_phone", ""),
            city=city,
            state=state,
            industry=industry,
            source_url=source_url,
            source_name=source_name,
        )
        for item in parser.records
    )


def fetch_public_html(url: str, *, timeout: int = 10, user_agent: str | None = None) -> str:
    """Fetch a public URL without bypassing access controls."""
    headers = {"User-Agent": user_agent or os.getenv("SAPHIRA_SCRAPER_USER_AGENT", "SaphiraLeadDiscovery/1.0")}
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - caller supplies an explicit public URL.
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Public source request failed: {exc}") from exc


def scrape_from_allowed_source(source_url: str, *, source_name: str, industry: str,
                               city: str = "", state: str = "", delay_seconds: float = 1.0,
                               timeout: int = 10) -> list[Lead]:
    """Fetch and parse an explicitly allowed fixture-compatible business source."""
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    text = fetch_public_html(source_url, timeout=timeout)
    return parse_fixture_html(
        text, source_url=source_url, source_name=source_name,
        industry=industry, city=city, state=state,
    )


def write_csv(leads: Iterable[Lead], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(lead) for lead in leads]
    fields = list(Lead.__dataclass_fields__.keys())
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return destination


def build_search_query(industry: str, location: str) -> str:
    """Build a query string for a separately configured, permitted search provider."""
    return quote_plus(f"{industry} in {location}")


if __name__ == "__main__":
    industry = os.getenv("SAPHIRA_LEAD_INDUSTRY", "Roofing Contractors")
    location = os.getenv("SAPHIRA_LEAD_LOCATION", "Tampa Bay, FL")
    output = Path(os.getenv("SAPHIRA_LEAD_OUTPUT", "storage/leads/tampa_bay_roofing_leads.csv"))
    print(f"Saphira lead discovery configuration: {industry} | {location}")
    print(f"Search query: {build_search_query(industry, location)}")
    print(f"Output path: {output}")
    print("No live source is selected by default. Configure an explicitly permitted source URL before network discovery.")
