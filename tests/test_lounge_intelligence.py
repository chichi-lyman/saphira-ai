# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
"""The Lounge-style intelligence blueprint stays complete and honest:
every source category is registered, each declares its access honestly,
and the community stack profile matches what the owner supplied."""

from src.intelligence.lounge_stack import (
    DATA_SOURCES,
    STACK_PROFILE,
    PROVIDER_ALIGNMENT,
    ingestion_readiness,
    source_by_id,
)


def test_all_five_source_categories_registered():
    categories = {s.category for s in DATA_SOURCES}
    assert categories == {
        "Private & Venture Market Data",
        "Investor & Partner Intelligence",
        "Public Markets & Indexes",
        "Unstructured Content Aggregation",
        "Agent Ecosystem Metrics",
    }


def test_private_data_is_marked_partnership_not_public():
    # Licensed directory/company data must never pretend to be a public feed.
    assert source_by_id("private_venture_market").access == "partnership"
    assert source_by_id("investor_partner_intelligence").access == "partnership"
    readiness = ingestion_readiness()
    assert set(readiness) == {"public_feed", "api_key", "partnership"}
    assert "unstructured_content" in readiness["public_feed"]


def test_stack_profile_matches_supplied_numbers():
    models = STACK_PROFILE["models_and_coding_assistants"]
    assert models["claude"] == 57.8
    assert models["claude_code"] == 54.6
    assert models["chatgpt"] == 48.6
    assert models["codex"] == 44.3
    assert models["gemini"] == 36.7
    assert models["ollama"] == 22.6
    assert models["github_copilot"] == 18.8
    assert models["cursor"] == 18.6
    infra = STACK_PROFILE["cloud_and_database"]
    assert infra["vercel"] == 28.9
    assert infra["supabase"] == 26.2


def test_every_stack_item_has_a_saphira_surface():
    for group in STACK_PROFILE.values():
        for item in group:
            assert item in PROVIDER_ALIGNMENT
    # Runtime alignment covers the providers Saphira actually runs.
    runtime = {v["saphira_surface"] for v in PROVIDER_ALIGNMENT.values() if v["kind"].startswith("runtime")}
    assert "provider:anthropic" in runtime
    assert "provider:openai" in runtime
    assert "provider:gemini" in runtime
    assert "endpoint:ollama_local" in runtime
