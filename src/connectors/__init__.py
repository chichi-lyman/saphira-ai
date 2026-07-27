# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

"""
Third-party connectors for Saphira AI.
Each connector abstracts a platform API and is designed to be called by agents.
"""

from .facebook import FacebookConnector
from .instagram import InstagramConnector
from .tiktok import TikTokConnector
from .linkedin import LinkedInConnector
from .gmail import GmailConnector
from .google_calendar import GoogleCalendarConnector
from .gemini import GeminiConnector

__all__ = [
    "FacebookConnector",
    "InstagramConnector",
    "TikTokConnector",
    "LinkedInConnector",
    "GmailConnector",
    "GoogleCalendarConnector",
    "GeminiConnector",
]
