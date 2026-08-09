import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import uuid

# Configure logging for Saphira core
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraOrchestrator")


@dataclass
class TaskResult:
    task_id: str
    status: str  # "completed", "failed", "pending"
    result: Any
    sub_agent: Optional[str] = None


class BaseSubAgent:
    """Abstract base class for Saphira sub-agents."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def execute(self, task_prompt: str, context: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Sub-agents must implement the async 'execute' method.")


class SaphiraOrchestrator:
    """
    Primary orchestration engine for Saphira AI.
    Routes requests, delegates to sub-agents, executes plugin tools, and handles background task queues.
    """

    def __init__(self, plugin_registry=None):
        self.plugin_registry = plugin_registry
        self.sub_agents: Dict[str, BaseSubAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, TaskResult] = {}

    def register_sub_agent(self, agent: BaseSubAgent):
        """Registers a specialized sub-agent (e.g., Code Reviewer, Web Researcher)."""
        self.sub_agents[agent.name] = agent
        logger.info(f"Registered sub-agent: {agent.name} - {agent.description}")

    async def process_user_intent(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing incoming prompts.
        Performs routing decisions: tool execution vs sub-agent delegation vs direct LLM response.
        """
        logger.info(f"Orchestrating intent for prompt: '{prompt[:50]}...'")
        
        # 1. Routing decision (Simple rule-based heuristic fallback or LLM classifier)
        target_agent = self._route_intent(prompt)

        if target_agent and target_agent in self.sub_agents:
            logger.info(f"Delegating task to specialized agent: {target_agent}")
            agent_result = await self.sub_agents[target_agent].execute(prompt, context)
            return {
                "source": target_agent,
                "status": "completed",
                "output": agent_result
            }

        # 2. Tool Execution via PluginRegistry
        if self.plugin_registry:
            # In production, pass prompt + tool schemas to LLM function caller here.
            pass

        # 3. Standard response return
        return {
            "source": "JARVIS_Core",
            "status": "completed",
            "output": f"Processed prompt directly: {prompt}"
        }

    def _route_intent(self, prompt: str) -> Optional[str]:
        """
        Determines the appropriate sub-agent based on intent matching.
        Can be upgraded to a fast-classifier LLM call or vector router.
        """
        p_lower = prompt.lower()
        if any(k in p_lower for k in ["code", "refactor", "bug", "git", "review"]):
            if "code_reviewer" in self.sub_agents:
                return "code_reviewer"
        elif any(k in p_lower for k in ["search", "scrape", "web", "lookup", "browser"]):
            if "web_researcher" in self.sub_agents:
                return "web_researcher"
        return None

    # --- Async Background Task Queue ---

    async def submit_background_task(self, prompt: str, callback_webhook: Optional[str] = None) -> str:
        """Enqueues a complex, multi-step task for async execution without blocking the user."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_result = TaskResult(task_id=task_id, status="pending", result=None)
        self.active_tasks[task_id] = task_result
        
        await self.task_queue.put((task_id, prompt, callback_webhook))
        logger.info(f"Background task {task_id} queued.")
        return task_id

    async def start_task_worker(self):
        """Worker loop that continuously processes background queued tasks."""
        logger.info("Starting background task worker loop...")
        while True:
            task_id, prompt, webhook = await self.task_queue.get()
            try:
                logger.info(f"Executing background task {task_id}...")
                result = await self.process_user_intent(prompt)
                
                self.active_tasks[task_id].status = "completed"
                self.active_tasks[task_id].result = result
                
                if webhook:
                    await self._notify_webhook(webhook, task_id, result)
                    
            except Exception as e:
                logger.error(f"Error processing task {task_id}: {str(e)}")
                self.active_tasks[task_id].status = "failed"
                self.active_tasks[task_id].result = str(e)
            finally:
                self.task_queue.task_done()

    async def _notify_webhook(self, webhook_url: str, task_id: str, result: Any):
        """Dispatches an alert/webhook upon background task completion."""
        logger.info(f"Pushing task alert for {task_id} to webhook: {webhook_url}")
        # Async HTTP POST implementation (e.g. using httpx or aiohttp) go here


# --- Example Sub-Agent Implementations for Testing ---

class CodeReviewerAgent(BaseSubAgent):
    def __init__(self):
        super().__init__("code_reviewer", "Analyzes, reviews, and refactors code.")

    async def execute(self, task_prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Code Reviewer logic
        return f"[Code Reviewer] Executed analysis for: {task_prompt}"


class WebResearcherAgent(BaseSubAgent):
    def __init__(self):
        super().__init__("web_researcher", "Browses the web and extracts structured info.")

    async def execute(self, task_prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Web search & DOM scrape logic
        return f"[Web Researcher] Extracted web insights for: {task_prompt}"

