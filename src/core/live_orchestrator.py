# Live Agent Orchestration Loop (Biometric-Aware)
# Copyright © 2026 Chelsea Megan Woods
#
# Thin wrapper that always injects the latest wearable biometrics
# and stress analysis before dispatching to any set of agents.

from typing import Dict, Any, Optional
import logging

from src.integrations.wearable_connector import wearable_connector
from src.agents.biometric_stress import BiometricStressDetector

logger = logging.getLogger("SaphiraLiveOrchestrator")


class LiveAgentOrchestrator:
    """
    Hooks live biometric readings directly into specialist agents
    (BoundaryCoach, AdminResolver, Relationship, LifestyleOrchestrator)
    so tone and workload recommendations adapt automatically.
    """

    def __init__(self, agents: Optional[Dict[str, Any]] = None):
        self.agents = agents or {}
        self.stress_detector = BiometricStressDetector()

    def register(self, name: str, agent: Any) -> None:
        self.agents[name] = agent

    async def process_user_intent_with_biometrics(
        self,
        user_intent: str,
        user_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        user_payload = user_payload or {}

        # 1. Live biometrics
        biometrics = wearable_connector.fetch_live_biometrics()

        # 2. Composite stress analysis
        stress_analysis = self.stress_detector.analyze(biometrics)
        stress_level = stress_analysis.get("stress_level", "medium")

        # 3. Shared context
        context = {
            "user_intent": user_intent,
            "text": user_intent,
            "message": user_intent,
            "raw_payload": user_payload,
            "biometrics": biometrics,
            "stress_analysis": stress_analysis,
            "stress_level": stress_level,
            "adaptation_guidance": stress_analysis.get("tone_guidance", "standard"),
            **user_payload,
        }

        # 4. Dispatch to every registered agent
        agent_responses: Dict[str, Any] = {}
        for name, agent in self.agents.items():
            try:
                if hasattr(agent, "safe_run"):
                    agent_responses[name] = await agent.safe_run(context)
                elif hasattr(agent, "run"):
                    agent_responses[name] = await agent.run(context)
                elif hasattr(agent, "execute"):
                    agent_responses[name] = await agent.execute(context)
                else:
                    agent_responses[name] = {
                        "status": "error",
                        "message": "No executable method on agent",
                    }
            except Exception as e:
                logger.exception("Agent %s failed in live orchestrator", name)
                agent_responses[name] = {
                    "status": "error",
                    "error": str(e),
                }

        return {
            "status": "success",
            "stress_level": stress_level,
            "stress_score": stress_analysis.get("stress_score"),
            "biometric_source": biometrics.get("source"),
            "biometrics": biometrics,
            "agent_outputs": agent_responses,
        }
