# Boundary & Difficult Conversation Coach
# Copyright © 2026 Chelsea Megan Woods

from typing import Dict, Any

class BoundaryCoachAgent:
    def __init__(self, router):
        self.router = router

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        situation = payload.get("situation", "")
        emotion = payload.get("emotion", "anxious")
        
        prompt = f"""You are Saphira's Boundary Coach.
User situation: {situation}
Current emotion: {emotion}

Draft 2-3 clear, firm but kind message options.
Simulate likely responses and suggest next steps.
Keep language warm, grounded, and free of fluff."""
        
        result = await self.router.generate_response(prompt)
        return {
            "status": "success",
            "agent": "boundary_coach",
            "suggestions": result,
            "category": "emotional"
        }
