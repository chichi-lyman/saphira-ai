# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.

import os
import requests
from typing import Dict, Any, Optional

class FacebookConnector:
    def __init__(self):
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID", "")
        self.base = "https://graph.facebook.com/v19.0"

    def post(self, message: str, link: Optional[str] = None) -> Dict[str, Any]:
        if not self.access_token or not self.page_id:
            return {"status": "error", "message": "Facebook credentials missing"}
        url = f"{self.base}/{self.page_id}/feed"
        payload = {"message": message, "access_token": self.access_token}
        if link:
            payload["link"] = link
        r = requests.post(url, data=payload, timeout=20)
        return r.json()
