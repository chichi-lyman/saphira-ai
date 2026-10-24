# Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.
# Owner & Creator: Chelsea Megan Woods | Woods AI Studio / Lyman Legacies / Nova Umbrella
"""Shopping connector — grocery, retail, Shopify / Shop Pay style flows."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


class ShoppingConnector:
    def __init__(self) -> None:
        self.shopify_token = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
        self.instacart_key = os.getenv("INSTACART_API_KEY", "")

    def health(self) -> Dict[str, Any]:
        configured = bool(self.shopify_token or self.instacart_key)
        return {
            "status": "ready" if configured else "unconfigured",
            "capabilities": ("shopping.grocery", "commerce.shopify"),
        }

    def grocery_from_list(
        self,
        items: List[str],
        *,
        store_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": "queued",
            "note": "Wire Instacart / grocery partner API",
            "items": items,
            "store_hint": store_hint,
        }

    def shopify_cart(
        self,
        shop_domain: str,
        line_items: List[Dict[str, Any]],
        *,
        user_confirmed: bool = False,
        virtual_card_ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not user_confirmed:
            return {
                "status": "needs_approval",
                "message": "Checkout requires explicit user confirmation via Cipher",
            }
        if virtual_card_ref and not str(virtual_card_ref).startswith("cred_"):
            return {"status": "error", "message": "Invalid virtual_card_ref"}
        return {
            "status": "queued",
            "note": "Wire Shopify Admin / Storefront + virtual card",
            "shop_domain": shop_domain,
            "line_items": line_items,
            "virtual_card_ref": virtual_card_ref,
        }
