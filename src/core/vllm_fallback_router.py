# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

"""Local vLLM / Ollama Fallback Router.

Hybrid cloud/local inference engine. Attempts cloud backends first and
seamlessly falls back to a local OpenAI-compatible endpoint (vLLM, Ollama,
LM Studio, llama.cpp) on timeout, network error, rate limit, or force_local.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger("SaphiraInferenceRouter")


class InferenceRequest(BaseModel):
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 1024
    force_local: bool = False


class SaphiraInferenceRouter:
    """
    Hybrid Cloud/Local Inference Engine for Saphira AI.
    Routes queries between cloud APIs and local vLLM/Ollama endpoints.
    """

    def __init__(
        self,
        cloud_api_url: str = "https://api.openai.com/v1/chat/completions",
        cloud_api_key: Optional[str] = None,
        local_vllm_url: str = "http://localhost:8000/v1/chat/completions",
        local_model_name: str = "qwen2.5-coder-7b-instruct",
    ) -> None:
        self.cloud_api_url = cloud_api_url
        self.cloud_api_key = cloud_api_key
        self.local_vllm_url = local_vllm_url
        self.local_model_name = local_model_name
        self.timeout = httpx.Timeout(8.0, connect=3.0)

    async def _execute_cloud_inference(
        self, request: InferenceRequest
    ) -> Dict[str, Any]:
        """Dispatches reasoning query to primary cloud backend."""
        headers = {"Content-Type": "application/json"}
        if self.cloud_api_key:
            headers["Authorization"] = f"Bearer {self.cloud_api_key}"

        payload = {
            "model": "gpt-4o",
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.cloud_api_url, json=payload, headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def _execute_local_inference(
        self, request: InferenceRequest
    ) -> Dict[str, Any]:
        """Dispatches reasoning query to local vLLM / Ollama instance."""
        logger.info(
            "[Inference Router] Executing via local endpoint: %s",
            self.local_vllm_url,
        )
        payload = {
            "model": self.local_model_name,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.post(self.local_vllm_url, json=payload)
            response.raise_for_status()
            return response.json()

    async def generate_response(
        self, request: InferenceRequest
    ) -> Dict[str, Any]:
        """
        Attempts cloud inference first; seamlessly falls back to local vLLM
        upon network disruption, timeout, or policy configuration.
        """
        if request.force_local or not self.cloud_api_key:
            return await self.execute_local_fallback(
                request, reason="Forced Local / Missing Cloud Key"
            )

        try:
            return await self._execute_cloud_inference(request)
        except (
            httpx.ConnectTimeout,
            httpx.ConnectError,
            httpx.ReadTimeout,
            httpx.HTTPStatusError,
        ) as err:
            return await self.execute_local_fallback(request, reason=str(err))

    async def execute_local_fallback(
        self, request: InferenceRequest, reason: str
    ) -> Dict[str, Any]:
        logger.warning("[Inference Fallback Triggered] Reason: %s", reason)
        try:
            result = await self._execute_local_inference(request)
            result["_routing_metadata"] = {
                "execution_mode": "local_fallback",
                "reason": reason,
            }
            return result
        except Exception as local_err:
            logger.error(
                "[Fatal Inference Error] Both cloud and local failed: %s",
                local_err,
            )
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": (
                                "Saphira Engine Error: Unable to reach cloud "
                                "backend or local vLLM fallback."
                            ),
                        }
                    }
                ],
                "_routing_metadata": {"execution_mode": "failed"},
            }
