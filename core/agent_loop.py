import asyncio
from core.orchestrator import SaphiraOrchestrator, CodeReviewerAgent, WebResearcherAgent
from tools.plugin_loader import PluginRegistry

async def main():
    registry = PluginRegistry()
    orchestrator = SaphiraOrchestrator(plugin_registry=registry)

    # Register sub-agents
    orchestrator.register_sub_agent(CodeReviewerAgent())
    orchestrator.register_sub_agent(WebResearcherAgent())

    # Start task worker loop in background
    asyncio.create_task(orchestrator.start_task_worker())

    # Test processing a code-related prompt
    response = await orchestrator.process_user_intent("Review this python function for memory leaks")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())

