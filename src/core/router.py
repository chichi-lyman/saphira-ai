# Enhanced Saphira Router with Expanded Intent Classifier + Wearable Support
# Copyright © 2026 Chelsea Megan Woods

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from google import genai
import openai

from src.core.intent_classifier import IntentClassifier
from src.integrations.wearable_connector import wearable

logger = logging.getLogger("SaphiraRouter")


class SaphiraAPIRouter:
    def __init__(self, primary_provider: str = "gemini", max_retries: int = 3):
        self.primary_provider = primary_provider.lower()
        self.max_retries = max_retries
        self.provider_health: Dict[str, bool] = {"gemini": True, "openai": True}
        self.intent_classifier = IntentClassifier()
        
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        
        self.gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None
        self.openai_client = openai.AsyncOpenAI(api_key=openai_key) if openai_key else None

    async def generate_response(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> str:
        providers_order = ["gemini", "openai"] if self.primary_provider == "gemini" else ["openai", "gemini"]
        last_exception = None

        for provider in providers_order:
            if not self.provider_health.get(provider, False):
                continue

            for attempt in range(1, self.max_retries + 1):
                try:
                    if provider == "gemini" and self.gemini_client:
                        loop = asyncio.get_event_loop()
                        res = await loop.run_in_executor(
                            None,
                            lambda: self.gemini_client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=prompt,
                                config={"system_instruction": system_instruction} if system_instruction else None
                            )
                        )
                        return res.text or "No response generated."

                    elif provider == "openai" and self.openai_client:
                        msgs = []
                        if system_instruction:
                            msgs.append({"role": "system", "content": system_instruction})
                        msgs.append({"role": "user", "content": prompt})
                        
                        res = await self.openai_client.chat.completions.create(
                            model="gpt-4o-mini", messages=msgs
                        )
                        return res.choices[0].message.content or "No response generated."

                except Exception as e:
                    last_exception = e
                    await asyncio.sleep(1.5 ** attempt)

            self.provider_health[provider] = False

        return f"[Saphira Standby Mode]: Request acknowledged. Error: {str(last_exception)}"

    def route_to_agent(self, text: str) -> str:
        """Use the expanded IntentClassifier instead of simple keywords."""
        return self.intent_classifier.route(text)

    async def enrich_with_biometrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically attach latest wearable data if not already present."""
        if "biometrics" not in payload or not payload["biometrics"]:
            payload["biometrics"] = await wearable.fetch_latest()
        return payload
