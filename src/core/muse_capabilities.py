# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""
Meta Muse parity capability registry for Saphira / Nova Umbrella.

Every entry is a routable capability key that NovaReign and the executive
orchestrator can claim. Status values:
  live   — core path or connector exists and is used in production paths
  stub   — contract + agent mapping defined; OAuth / vendor API pending
  planned — documented only

External / commercial / credential capabilities default to REQUIRE_APPROVAL
and must pass Agent Cipher (Sentinel) before execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class CapStatus(str, Enum):
    LIVE = "live"
    STUB = "stub"
    PLANNED = "planned"


class AutonomyFloor(str, Enum):
    OBSERVE = "OBSERVE"
    ASSIST = "ASSIST"
    EXECUTE = "EXECUTE"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


@dataclass(frozen=True)
class MuseCapability:
    key: str
    description: str
    primary_agent: str
    supporting_agents: tuple[str, ...] = ()
    status: CapStatus = CapStatus.STUB
    autonomy: AutonomyFloor = AutonomyFloor.ASSIST
    external_side_effect: bool = False
    requires_cipher: bool = False
    muse_category: str = "core"
    tags: tuple[str, ...] = ()


MUSE_CAPABILITIES: Dict[str, MuseCapability] = {}


def _reg(cap: MuseCapability) -> None:
    MUSE_CAPABILITIES[cap.key] = cap


# --- Core agent behavior ---
_reg(MuseCapability(
    "goal.decompose_and_execute",
    "Accept a high-level goal, produce a multi-step plan, and execute under governance",
    "saphira",
    ("novareign", "agent_zero"),
    CapStatus.LIVE,
    AutonomyFloor.ASSIST,
    muse_category="core",
    tags=("plan", "muse-parity"),
))
_reg(MuseCapability(
    "goal.background_continue",
    "Continue work after session close; notify on approval or completion",
    "novareign",
    ("novaaethrea",),
    CapStatus.STUB,
    AutonomyFloor.EXECUTE,
    muse_category="core",
    tags=("background", "muse-parity"),
))
_reg(MuseCapability(
    "goal.sensitive_approval",
    "System approval dialog before messages, purchases, data sharing",
    "cipher",
    ("agent_two",),
    CapStatus.LIVE,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="core",
    tags=("sentinel", "muse-parity"),
))
_reg(MuseCapability(
    "goal.watch_and_intervene",
    "Open live sandbox session, pause, take control, or stop task",
    "cipher",
    ("agent_zero",),
    CapStatus.STUB,
    AutonomyFloor.ASSIST,
    muse_category="core",
    tags=("sandbox", "muse-parity"),
))

# --- Web & computer use ---
_reg(MuseCapability(
    "web.isolated_browse",
    "Browse in isolated sandbox (local Playwright / Docker / cloud)",
    "cipher",
    ("agent_two",),
    CapStatus.LIVE,
    AutonomyFloor.EXECUTE,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="web",
    tags=("sandbox", "muse-parity"),
))
_reg(MuseCapability(
    "web.fill_forms",
    "Fill forms and interact across sites under Sentinel review",
    "cipher",
    ("agent_two", "agent_zero"),
    CapStatus.LIVE,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="web",
    tags=("sandbox", "muse-parity"),
))
_reg(MuseCapability(
    "desktop.mac_apps",
    "Opt-in control of native Mac apps (Mail, Calendar, Messages, Notes)",
    "agent_zero",
    (),
    CapStatus.PLANNED,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="web",
    tags=("desktop", "muse-parity"),
))

# --- Communication ---
_reg(MuseCapability(
    "comm.email_read_draft_send",
    "Read, draft, and send email via Gmail / Outlook; strip reset links",
    "novaaethrea",
    ("agent_zero", "cipher"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="communication",
    tags=("email", "muse-parity"),
))
_reg(MuseCapability(
    "comm.calendar_manage",
    "Read and create calendar events (Google / Outlook)",
    "novaaethrea",
    ("agent_zero",),
    CapStatus.STUB,
    AutonomyFloor.EXECUTE,
    external_side_effect=True,
    muse_category="communication",
    tags=("calendar", "muse-parity"),
))
_reg(MuseCapability(
    "comm.messaging",
    "Message via WhatsApp, Telegram, SMS, or in-app channels",
    "novaaethrea",
    ("agent_zero", "cipher"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="communication",
    tags=("messaging", "muse-parity"),
))

# --- Travel, local, everyday ---
_reg(MuseCapability(
    "travel.book",
    "Search and book flights / hotels (Expedia-style connector)",
    "apex",
    ("agent_zero", "cipher"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="travel",
    tags=("travel", "muse-parity"),
))
_reg(MuseCapability(
    "local.reserve",
    "Restaurant / table bookings (OpenTable-style)",
    "instinct",
    ("agent_zero", "cipher"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="local",
    tags=("local", "muse-parity"),
))
_reg(MuseCapability(
    "local.directions_wait",
    "Directions, wait times, local discovery",
    "instinct",
    ("aura",),
    CapStatus.STUB,
    AutonomyFloor.ASSIST,
    muse_category="local",
    tags=("local", "muse-parity"),
))
_reg(MuseCapability(
    "shopping.grocery",
    "Grocery lists and Instacart-style ordering",
    "instinct",
    ("lyra", "agent_zero"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="shopping",
    tags=("shopping", "muse-parity"),
))
_reg(MuseCapability(
    "health.fitness",
    "Fitness / Peloton-style session and schedule helpers",
    "lyra",
    (),
    CapStatus.PLANNED,
    AutonomyFloor.ASSIST,
    muse_category="health",
    tags=("health", "muse-parity"),
))

# --- Shopping & money ---
_reg(MuseCapability(
    "commerce.virtual_card_purchase",
    "Purchase with one-time virtual card (Stripe Link style); merchant never sees real card",
    "apex",
    ("cipher", "agent_zero"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="commerce",
    tags=("payment", "muse-parity"),
))
_reg(MuseCapability(
    "commerce.shopify",
    "Shopify / Shop Pay store interactions",
    "apex",
    ("agent_zero",),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="commerce",
    tags=("shopping", "muse-parity"),
))
_reg(MuseCapability(
    "commerce.negotiate",
    "Negotiate bills or selling prices",
    "apex",
    ("instinct", "cipher"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="commerce",
    tags=("negotiate", "muse-parity"),
))
_reg(MuseCapability(
    "finance.plaid_quickbooks",
    "Plaid bank link and QuickBooks small-business flows",
    "lyra",
    ("apex", "cipher"),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="finance",
    tags=("finance", "muse-parity"),
))

# --- Productivity & work ---
_reg(MuseCapability(
    "productivity.docs_dashboards",
    "Create documents, PDFs, dashboards, simple web pages",
    "aura",
    ("agent_zero",),
    CapStatus.STUB,
    AutonomyFloor.EXECUTE,
    muse_category="productivity",
    tags=("docs", "muse-parity"),
))
_reg(MuseCapability(
    "productivity.reminders_goals",
    "Reminders, goal tracking, ambient monitors (weather, etc.)",
    "novaaethrea",
    ("saphira",),
    CapStatus.STUB,
    AutonomyFloor.EXECUTE,
    muse_category="productivity",
    tags=("reminders", "muse-parity"),
))
_reg(MuseCapability(
    "productivity.work_connectors",
    "Notion, Slack, Zoom, Asana, Box, Dropbox, Figma, Canva, GitHub, etc.",
    "novaaethrea",
    ("agent_zero",),
    CapStatus.STUB,
    AutonomyFloor.EXECUTE,
    external_side_effect=True,
    muse_category="productivity",
    tags=("connectors", "muse-parity"),
))
_reg(MuseCapability(
    "memory.preference_editable",
    "Remember preferences; user can read, edit, forget",
    "novaaethrea",
    ("saphira",),
    CapStatus.LIVE,
    AutonomyFloor.EXECUTE,
    muse_category="memory",
    tags=("memory", "muse-parity"),
))
_reg(MuseCapability(
    "activity.full_log",
    "Full activity / plan history for transparency and audit",
    "novareign",
    ("cipher",),
    CapStatus.STUB,
    AutonomyFloor.OBSERVE,
    muse_category="governance",
    tags=("audit", "muse-parity"),
))

# --- Creative & media ---
_reg(MuseCapability(
    "creative.qa_and_images",
    "Answer questions and generate images",
    "saphira",
    ("aura",),
    CapStatus.LIVE,
    AutonomyFloor.EXECUTE,
    muse_category="creative",
    tags=("imagine", "muse-parity"),
))
_reg(MuseCapability(
    "creative.recipe_to_grocery",
    "Turn recipe content / reels into grocery lists and menus",
    "aura",
    ("instinct",),
    CapStatus.STUB,
    AutonomyFloor.ASSIST,
    muse_category="creative",
    tags=("recipe", "muse-parity"),
))
_reg(MuseCapability(
    "social.meta_catalog",
    "Instagram / Facebook / Meta Catalog content and commerce helpers",
    "instinct",
    ("aura",),
    CapStatus.STUB,
    AutonomyFloor.EXECUTE,
    external_side_effect=True,
    muse_category="social",
    tags=("social", "muse-parity"),
))

# --- Small business ---
_reg(MuseCapability(
    "business.one_click_connectors",
    "One-click business connectors (Asana, Box, Canva, QuickBooks, Shopify, Slack, Stripe, Zoom…)",
    "apex",
    ("novaaethrea",),
    CapStatus.STUB,
    AutonomyFloor.EXECUTE,
    external_side_effect=True,
    muse_category="business",
    tags=("smb", "muse-parity"),
))
_reg(MuseCapability(
    "business.meta_ads_pages",
    "Facebook Page, Instagram professional, Meta ad account linking",
    "instinct",
    ("apex",),
    CapStatus.STUB,
    AutonomyFloor.REQUIRE_APPROVAL,
    external_side_effect=True,
    requires_cipher=True,
    muse_category="business",
    tags=("ads", "muse-parity"),
))


def list_by_category(category: str) -> List[MuseCapability]:
    return [c for c in MUSE_CAPABILITIES.values() if c.muse_category == category]


def list_by_agent(agent: str) -> List[MuseCapability]:
    agent = agent.lower()
    return [
        c
        for c in MUSE_CAPABILITIES.values()
        if c.primary_agent == agent or agent in c.supporting_agents
    ]


def list_requiring_cipher() -> List[MuseCapability]:
    return [c for c in MUSE_CAPABILITIES.values() if c.requires_cipher]


def summary() -> Dict[str, int]:
    counts: Dict[str, int] = {"live": 0, "stub": 0, "planned": 0, "total": 0}
    for c in MUSE_CAPABILITIES.values():
        counts[c.status.value] += 1
        counts["total"] += 1
    return counts
