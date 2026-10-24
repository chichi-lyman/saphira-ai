# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""Travel connector (Expedia-style flights / hotels).

All booking actions must pass Agent Cipher (Sentinel) and require user
approval before any charge or reservation is confirmed.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional


class TravelConnector:
    """Search and book travel. Production wiring uses partner APIs + virtual card."""

    def __init__(self) -> None:
        self.api_key = os.getenv("TRAVEL_API_KEY", "")
        self.provider = os.getenv("TRAVEL_PROVIDER", "stub")

    def health(self) -> Dict[str, Any]:
        return {
            "status": "ready" if self.api_key else "unconfigured",
            "provider": self.provider,
            "capabilities": ("travel.book", "travel.search"),
        }

    def search_flights(
        self,
        origin: str,
        destination: str,
        depart_date: str,
        *,
        return_date: Optional[str] = None,
        passengers: int = 1,
    ) -> Dict[str, Any]:
        if not origin or not destination:
            return {"status": "error", "message": "origin and destination required"}
        return {
            "status": "queued",
            "note": "Wire partner flight search API",
            "origin": origin,
            "destination": destination,
            "depart_date": depart_date,
            "return_date": return_date,
            "passengers": passengers,
            "results": [],
        }

    def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        *,
        guests: int = 1,
    ) -> Dict[str, Any]:
        return {
            "status": "queued",
            "note": "Wire partner hotel search API",
            "location": location,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "results": [],
        }

    def book(
        self,
        offer_id: str,
        *,
        traveler_name: str,
        virtual_card_ref: Optional[str] = None,
        user_confirmed: bool = False,
    ) -> Dict[str, Any]:
        if not user_confirmed:
            return {
                "status": "needs_approval",
                "message": "Booking requires explicit user confirmation via Cipher",
                "offer_id": offer_id,
            }
        if not virtual_card_ref or not str(virtual_card_ref).startswith("cred_"):
            return {
                "status": "error",
                "message": "Zero-trust virtual_card_ref required",
            }
        return {
            "status": "queued",
            "note": "Wire confirmed booking + Stripe Link / virtual card charge",
            "offer_id": offer_id,
            "traveler_name": traveler_name,
            "virtual_card_ref": virtual_card_ref,
        }
