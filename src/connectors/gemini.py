# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.

import os
from typing import Dict, Any, Optional

class GeminiConnector:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")

    def generate(self, prompt: str, model: str = "gemini-2.0-flash") -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "message": "GEMINI_API_KEY missing"}
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            res = client.models.generate_content(model=model, contents=prompt)
            return {"status": "success", "text": res.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
