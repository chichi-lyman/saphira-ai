# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""Lounge-style intelligence stack for Saphira AI.

Owner directive (2026-10-23): plug the Lounge AI intelligence blueprint into
Saphira — its data-source categories, tracking model, query surface, and the
member developer-stack profile.

IMPORTANT: this module is the *blueprint and registry*, not a copy of any
third party's private data. Lounge AI's company profiles, investor directory,
and partner contact data live inside Lounge and are licensed/partnership data;
each source below declares exactly what access it needs before live records can
flow. Public feeds can be connected without any partnership.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# 1. Data ingestion & tracking sources
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DataSource:
    id: str
    category: str
    description: str
    tracks: tuple[str, ...]
    # public_feed  -> can be connected today, no partnership needed
    # api_key      -> needs the owner's own key/account for that provider
    # partnership  -> needs a license/partnership with the data owner
    access: str
    status: str = "registered"  # registered | connected


DATA_SOURCES: tuple[DataSource, ...] = (
    DataSource(
        id="private_venture_market",
        category="Private & Venture Market Data",
        description=(
            "Private AI company intelligence in the Lounge model: 600+ AI company "
            "profiles, Series A+ funding rounds, valuations, acquisitions and M&A "
            "exits, plus an AI Revenue Leaderboard ranking private AI companies by ARR."
        ),
        tracks=("companies", "funding_rounds", "valuations", "acquisitions", "mna_exits", "arr_leaderboard"),
        access="partnership",
    ),
    DataSource(
        id="investor_partner_intelligence",
        category="Investor & Partner Intelligence",
        description=(
            "Directory intelligence in the Lounge model: 1,100+ AI venture firms and "
            "14,000+ individual partner/staff profiles with investment focus. Direct "
            "contact details and LinkedIn handles are licensed data and only flow "
            "under a partnership; firm-level focus data can be built from public sources."
        ),
        tracks=("venture_firms", "partners", "investment_focus", "contact_info_licensed_only"),
        access="partnership",
    ),
    DataSource(
        id="public_markets_index",
        category="Public Markets & Indexes",
        description=(
            "Public tech/AI equity monitoring with a proprietary index slot "
            "(Lounge AI Index pattern) — Saphira keeps her own AI index watchlist here."
        ),
        tracks=("public_ai_equities", "index_components", "price_moves"),
        access="api_key",
    ),
    DataSource(
        id="unstructured_content",
        category="Unstructured Content Aggregation",
        description=(
            "Full-text industry reports (Stanford AI Index — public; PitchBook, BOND, "
            "a16z, Goldman Sachs — mixed public/licensed), searchable newsletter "
            "archives, podcast transcripts/episodes, and tagged educational "
            "YouTube videos and Shorts, indexed for query."
        ),
        tracks=("industry_reports", "newsletters", "podcast_transcripts", "youtube_educational"),
        access="public_feed",
    ),
    DataSource(
        id="agent_ecosystem_metrics",
        category="Agent Ecosystem Metrics",
        description=(
            "Catalog of the most-installed agent skills, software tools, and "
            "accelerator perks across the agent ecosystem — Nova Umbrella reads "
            "this to know which skills the market actually runs."
        ),
        tracks=("installed_agent_skills", "software_tools", "accelerator_perks"),
        access="public_feed",
    ),
)


def source_by_id(source_id: str) -> Optional[DataSource]:
    for source in DATA_SOURCES:
        if source.id == source_id:
            return source
    return None


def ingestion_readiness() -> Dict[str, List[str]]:
    """Group source ids by the access each one needs before live data flows."""
    groups: Dict[str, List[str]] = {"public_feed": [], "api_key": [], "partnership": []}
    for source in DATA_SOURCES:
        groups.setdefault(source.access, []).append(source.id)
    return groups


# ---------------------------------------------------------------------------
# 2. Member & ecosystem developer stack (Lounge community profile)
# ---------------------------------------------------------------------------

# Adoption shares across the Lounge founder community, as supplied by the
# owner 2026-10-23. These describe the community's stack — Saphira's own
# runtime alignment is in PROVIDER_ALIGNMENT below.
STACK_PROFILE: Dict[str, Dict[str, float]] = {
    "models_and_coding_assistants": {
        "claude": 57.8,
        "claude_code": 54.6,
        "chatgpt": 48.6,
        "codex": 44.3,
        "gemini": 36.7,
        "ollama": 22.6,
        "github_copilot": 18.8,
        "cursor": 18.6,
    },
    "cloud_and_database": {
        "vercel": 28.9,
        "supabase": 26.2,
    },
}

# How the community stack maps onto Saphira's own systems.
# Runtime providers plug into src.providers.registry; coding assistants are
# developer-workflow tools, not runtime providers, and are recorded as such.
PROVIDER_ALIGNMENT: Dict[str, Dict[str, str]] = {
    "claude": {"saphira_surface": "provider:anthropic", "kind": "runtime"},
    "claude_code": {"saphira_surface": "developer_workflow", "kind": "dev_tool"},
    "chatgpt": {"saphira_surface": "provider:openai", "kind": "runtime"},
    "codex": {"saphira_surface": "developer_workflow", "kind": "dev_tool"},
    "gemini": {"saphira_surface": "provider:gemini", "kind": "runtime"},
    "ollama": {"saphira_surface": "endpoint:ollama_local", "kind": "runtime_local"},
    "github_copilot": {"saphira_surface": "developer_workflow", "kind": "dev_tool"},
    "cursor": {"saphira_surface": "developer_workflow", "kind": "dev_tool"},
    "vercel": {"saphira_surface": "deploy_target", "kind": "infrastructure"},
    "supabase": {"saphira_surface": "database_backend", "kind": "infrastructure"},
}
