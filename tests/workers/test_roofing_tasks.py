from workers.roofing_tasks import prepare_roofing_outreach, research_roofing_prospect


def test_roofing_research_normalizes_seed():
    result = research_roofing_prospect.run({
        "id": "fixture-001",
        "business_name": "Fixture Roofing",
        "city": "Tampa",
        "state": "FL",
        "source": "fixture",
    })

    assert result["prospect_id"] == "fixture-001"
    assert result["status"] == "RESEARCH_READY"


def test_outreach_is_queued_for_approval():
    result = prepare_roofing_outreach.run({
        "prospect_id": "fixture-002",
        "business_name": "Fixture Roofing 2",
        "channel": "email",
        "draft": "A governed fixture draft.",
    })

    assert result["status"] == "REQUIRE_APPROVAL"
    assert result["approval_id"]
