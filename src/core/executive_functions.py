# Narrow Divergent Executive Functions for Agent Refinement
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any, List

class ExecutiveFunctionModule:
    """
    Implements narrow, specialized executive functions used by agents:
    - Working memory prioritization
    - Cognitive flexibility (switching strategies)
    - Inhibitory control (filtering noise)
    - Planning & sequencing
    """

    def prioritize_working_memory(self, items: List[str], capacity: int = 5) -> List[str]:
        """Keep only the most relevant items in active context."""
        return items[:capacity]

    def switch_strategy(self, current_approach: str, failure_count: int) -> str:
        """Divergent thinking: try a different path after repeated failure."""
        if failure_count >= 2:
            return "alternative_path"
        return current_approach

    def inhibit_noise(self, candidates: List[str], relevance_scores: List[float], threshold: float = 0.6) -> List[str]:
        """Filter out low-relevance suggestions."""
        return [c for c, s in zip(candidates, relevance_scores) if s >= threshold]

    def sequence_plan(self, goal: str, steps: List[str]) -> Dict[str, Any]:
        """Order steps for minimal cognitive load."""
        return {
            "goal": goal,
            "ordered_steps": steps,
            "estimated_effort": "low" if len(steps) <= 3 else "medium"
        }
