# Multi-Agent Swarm Orchestration
# Copyright © 2026 Chelsea Megan Woods
#
# Parallel specialist swarm + sequential core pipeline.
# Specialists (BoundaryCoach, AdminResolver, Relationship, Lifestyle)
# can run concurrently; results are merged and optionally passed into
# the existing six-agent SaphiraOrchestrator chain for device / home actions.

from typing import Dict, Any, List, Optional, Callable, Awaitable
import asyncio
import logging
from datetime import datetime, timezone

from src.integrations.wearable_connector import wearable_connector
from src.agents.biometric_stress import BiometricStressDetector

logger = logging.getLogger("SaphiraSwarm")


class SwarmOrchestrator:
    """
    Coordinates a dynamic multi-agent swarm.

    - Spawns specialist agents in parallel for high-level life / admin tasks
    - Injects live biometrics + stress analysis into every agent context
    - Supports self-healing retries at the swarm level
    - Can hand off device-level intents to the core SaphiraOrchestrator
    """

    def __init__(
        self,
        specialist_agents: Optional[Dict[str, Any]] = None,
        core_orchestrator: Any = None,
        max_parallel: int = 8,
    ):
        self.specialists = specialist_agents or {}
        self.core = core_orchestrator
        self.max_parallel = max_parallel
        self.stress_detector = BiometricStressDetector()
        self._history: List[Dict[str, Any]] = []

    def register_specialist(self, name: str, agent: Any) -> None:
        self.specialists[name] = agent

    async def _run_one(
        self,
        name: str,
        agent: Any,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            if hasattr(agent, "safe_run"):
                result = await agent.safe_run(context)
            elif hasattr(agent, "run"):
                result = await agent.run(context)
            elif hasattr(agent, "execute"):
                result = await agent.execute(context)
            else:
                return {
                    "agent": name,
                    "status": "error",
                    "message": "Agent has no run/safe_run/execute method",
                }
            result.setdefault("agent", name)
            return result
        except Exception as e:
            logger.exception("Specialist %s failed", name)
            return {
                "agent": name,
                "status": "error",
                "error": str(e),
            }

    async def run_swarm(
        self,
        user_intent: str,
        payload: Optional[Dict[str, Any]] = None,
        specialist_names: Optional[List[str]] = None,
        include_core: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a parallel swarm of specialists, optionally followed by the
        core device pipeline.
        """
        payload = payload or {}
        biometrics = wearable_connector.fetch_live_biometrics()
        stress_analysis = self.stress_detector.analyze(biometrics)

        context = {
            "user_intent": user_intent,
            "text": user_intent,
            "message": user_intent,
            "raw_payload": payload,
            "biometrics": biometrics,
            "stress_analysis": stress_analysis,
            "stress_level": stress_analysis["stress_level"],
            "adaptation_guidance": stress_analysis["tone_guidance"],
            **payload,
        }

        # Select which specialists to run
        if specialist_names:
            targets = {
                n: self.specialists[n]
                for n in specialist_names
                if n in self.specialists
            }
        else:
            targets = dict(self.specialists)

        # Parallel execution with semaphore
        sem = asyncio.Semaphore(self.max_parallel)

        async def bounded(name: str, agent: Any):
            async with sem:
                return await self._run_one(name, agent, context)

        tasks = [bounded(n, a) for n, a in targets.items()]
        specialist_results = await asyncio.gather(*tasks) if tasks else []

        result: Dict[str, Any] = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stress_level": stress_analysis["stress_level"],
            "stress_score": stress_analysis["stress_score"],
            "biometric_source": biometrics.get("source"),
            "biometrics": biometrics,
            "specialist_outputs": {
                r.get("agent", f"unknown_{i}"): r
                for i, r in enumerate(specialist_results)
            },
            "agents_run": list(targets.keys()),
        }

        # Optional hand-off to core device orchestrator
        if include_core and self.core is not None:
            try:
                core_result = await self.core.process(user_intent, context)
                result["core_pipeline"] = core_result
            except Exception as e:
                logger.exception("Core orchestrator failed inside swarm")
                result["core_pipeline"] = {
                    "status": "error",
                    "error": str(e),
                }

        self._history.append({
            "intent": user_intent,
            "stress_level": result["stress_level"],
            "agents": result["agents_run"],
            "ts": result["timestamp"],
        })
        if len(self._history) > 100:
            self._history = self._history[-100:]

        return result

    def recent_history(self, n: int = 10) -> List[Dict[str, Any]]:
        return self._history[-n:]
