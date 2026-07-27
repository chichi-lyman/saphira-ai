# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.

import os
import requests
from typing import Dict, Any

class LinkedInConnector:
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.author_urn = os.getenv("LINKEDIN_AUTHOR_URN", "")  # urn:li:person:xxxx

    def post(self, text: str) -> Dict[str, Any]:
        if not self.access_token or not self.author_urn:
            return {"status": "error", "message": "LinkedIn credentials missing"}
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        body = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        r = requests.post(url, json=body, headers=headers, timeout=20)
        return r.json()
