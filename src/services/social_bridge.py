# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Social Media Cross-Posting & Account Bridge
Pushes video reels, posts, and ads across connected platforms via n8n/Make webhooks.
"""

import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("SaphiraSocialBridge")


class SocialMediaBridge:
    def __init__(self, webhook_url: Optional[str] = None):
        self.creator = "Chelsea Megan Woods"
        self.copyright = "Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved."
        self.tiktok_account = "https://www.tiktok.com/@chelseameganwoods"
        self.n8n_webhook_url = webhook_url or "https://automation.woodsaistudio.com/webhook/cross-post"

    def publish_viral_campaign(
        self,
        video_url: str,
        caption: str,
        hashtags: List[str],
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        if platforms is None:
            platforms = [
                "tiktok",
                "instagram_reels",
                "facebook_page",
                "youtube_shorts",
                "linkedin"
            ]

        payload = {
            "author": self.creator,
            "copyright": self.copyright,
            "video_url": video_url,
            "caption": f"{caption}\n\nCreated by Chelsea Megan Woods | Saphira AI",
            "hashtags": hashtags,
            "platforms": platforms
        }

        try:
            response = requests.post(self.n8n_webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            logger.info(f"Campaign published to {platforms}")
            return response.json()
        except Exception as e:
            logger.error(f"Social bridge error: {e}")
            return {"status": "error", "message": str(e)}

    def build_ad_copy(self) -> Dict[str, str]:
        """Pre-built high-converting ad copy matrix."""
        return {
            "headline_1": "Saphira AI: Speak Upfront. Automate in Silence.",
            "headline_2": "The Conversational AI Created by Chelsea Megan Woods",
            "primary_text": (
                "Stop toggling between 10 different apps. Talk to Saphira naturally "
                "while she silently runs your code, manages 3D printers, and controls "
                "your smart home in the background. Simplify your day by 1% every single time."
            ),
            "negative_keywords": "free download crack, open source clone, free github bot, cheap template"
        }
