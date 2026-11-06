"""
Capability registry entries for web access, synthesis, and ambient features.
Copyright © 2026 Chelsea Megan Woods.

These IDs are registered with NovaReign / the Capability Registry so
routing stays consistent with the 1,000-capability catalog.
"""

WEB_AND_AMBIENT_CAPABILITIES = [
    {
        "id": "web_search",
        "description": "Query a search API and return titles, links, and snippets",
        "agent": "scholar",
        "requires_network": True,
        "policy": "allow_public",
    },
    {
        "id": "fetch_page",
        "description": "Responsibly fetch a single public page after robots.txt check",
        "agent": "scholar",
        "requires_network": True,
        "policy": "allow_public",
    },
    {
        "id": "refresh_page",
        "description": "Incremental re-fetch of a previously seen public URL",
        "agent": "scholar",
        "requires_network": True,
        "policy": "allow_public",
    },
    {
        "id": "synthesize_research",
        "description": "Summarize multi-source results into structured findings",
        "agent": "scholar",
        "requires_network": False,
        "policy": "allow",
    },
    {
        "id": "cast_to_display",
        "description": "Cast map, article, or image to nearby TV / smart display",
        "agent": "zero",
        "requires_network": True,
        "policy": "require_approval_first_use",
    },
    {
        "id": "push_to_device",
        "description": "Open map or article on phone or laptop",
        "agent": "zero",
        "requires_network": False,
        "policy": "allow",
    },
    {
        "id": "start_trivia",
        "description": "Start a spontaneous topic-based trivia round",
        "agent": "scholar",
        "requires_network": False,
        "policy": "allow",
    },
    {
        "id": "set_ambient_music",
        "description": "Queue background music matching conversation tone",
        "agent": "zero",
        "requires_network": True,
        "policy": "allow",
    },
]
