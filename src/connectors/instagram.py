# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.

import os
import requests
from typing import Dict, Any

class InstagramConnector:
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.ig_user_id = os.getenv("INSTAGRAM_USER_ID", "")
        self.base = "https://graph.facebook.com/v19.0"

    def create_media_container(self, image_url: str, caption: str) -> Dict[str, Any]:
        if not self.access_token or not self.ig_user_id:
            return {"status": "error", "message": "Instagram credentials missing"}
        url = f"{self.base}/{self.ig_user_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        r = requests.post(url, data=payload, timeout=20)
        return r.json()
