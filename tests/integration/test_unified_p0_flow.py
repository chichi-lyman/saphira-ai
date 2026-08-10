from src.core.saphira_unified_runtime import build_task_graph
from src.integrations.p0_adapters import ASICoreAdapter, SalesSwarmAdapter, SentinelAdapter


def test_unified_p0_flow():
    request = "Find qualified HVAC prospects and prepare a safe outreach plan."
    directive = ASICoreAdapter().formulate_directive(request)
    tasks = build_task_graph(request, ["research", "sales", "quality_assurance"])

    sales_plan = SalesSwarmAdapter().plan("Commercial HVAC", "Atlanta, GA", 5)
    security = SentinelAdapter().scan("saphira-sales-swarm", {"failed_auth_attempts": 0})

    assert directive["status"] == "DIRECTIVE_FORMULATED"
    assert [task.capability for task in tasks] == ["research", "sales", "quality_assurance"]
    assert sales_plan["status"] == "PENDING_APPROVAL"
    assert security["threat_status"] == "GREEN"
