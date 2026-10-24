# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

"""NovaReign UI Screen Parser.

Translates raw Android accessibility node hierarchies into structured,
actionable UI maps for Saphira's automation pipeline.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

logger = logging.getLogger("NovaReignParser")


class UINode(BaseModel):
    node_id: Optional[str] = None
    text: Optional[str] = None
    content_desc: Optional[str] = None
    class_name: str
    is_clickable: bool = False
    is_editable: bool = False
    is_scrollable: bool = False
    bounds_in_screen: Tuple[int, int, int, int] = Field(
        default=(0, 0, 0, 0),
        description="Coordinates (left, top, right, bottom)",
    )
    center_point: Tuple[int, int] = Field(
        default=(0, 0),
        description="Calculated (X, Y) center for touch dispatch",
    )
    children: List["UINode"] = Field(default_factory=list)


class ParsedScreenState(BaseModel):
    package_name: str
    interactive_elements: List[UINode]
    scrollable_elements: List[UINode]
    focused_input: Optional[UINode] = None


class NovaReignScreenParser:
    """
    NovaReign Sub-Agent UI Layout Parser.
    Compresses raw Android accessibility trees into actionable element maps.
    """

    INTERACTIVE_CLASSES = {
        "android.widget.Button",
        "android.widget.EditText",
        "android.widget.CheckBox",
        "android.widget.ImageButton",
        "android.widget.ImageView",
        "android.widget.TextView",
    }

    @classmethod
    def calculate_center(cls, bounds: Tuple[int, int, int, int]) -> Tuple[int, int]:
        left, top, right, bottom = bounds
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        return center_x, center_y

    @classmethod
    def parse_raw_tree(cls, raw_payload: Dict[str, Any]) -> ParsedScreenState:
        """
        Parses raw accessibility payload into a pruned, actionable UI state.
        """
        package_name = raw_payload.get("package_name", "unknown")
        interactive_nodes: List[UINode] = []
        scrollable_nodes: List[UINode] = []
        focused_input: Optional[UINode] = None

        def traverse(node_data: Dict[str, Any]) -> None:
            nonlocal focused_input
            class_name = node_data.get("class_name", "")
            text = node_data.get("text")
            desc = node_data.get("content_desc")
            clickable = node_data.get("is_clickable", False)
            editable = node_data.get("is_editable", False)
            scrollable = node_data.get("is_scrollable", False)

            raw_bounds = node_data.get("bounds", [0, 0, 0, 0])
            if len(raw_bounds) < 4:
                raw_bounds = [0, 0, 0, 0]
            bounds_tuple = (
                int(raw_bounds[0]),
                int(raw_bounds[1]),
                int(raw_bounds[2]),
                int(raw_bounds[3]),
            )
            center = cls.calculate_center(bounds_tuple)

            ui_node = UINode(
                node_id=node_data.get("view_id_resource_name"),
                text=text,
                content_desc=desc,
                class_name=class_name,
                is_clickable=clickable,
                is_editable=editable,
                is_scrollable=scrollable,
                bounds_in_screen=bounds_tuple,
                center_point=center,
            )

            is_valid_label = bool(text and str(text).strip()) or bool(
                desc and str(desc).strip()
            )
            if (clickable or editable or is_valid_label) and bounds_tuple != (
                0,
                0,
                0,
                0,
            ):
                interactive_nodes.append(ui_node)

            if scrollable:
                scrollable_nodes.append(ui_node)

            if editable and node_data.get("is_focused", False):
                focused_input = ui_node

            for child in node_data.get("children", []):
                if isinstance(child, dict):
                    traverse(child)

        root_node = raw_payload.get("root_node", {})
        if root_node:
            traverse(root_node)

        logger.info(
            "[NovaReign] Parsed package=%s interactive=%d scrollable=%d",
            package_name,
            len(interactive_nodes),
            len(scrollable_nodes),
        )

        return ParsedScreenState(
            package_name=package_name,
            interactive_elements=interactive_nodes,
            scrollable_elements=scrollable_nodes,
            focused_input=focused_input,
        )

    @classmethod
    def resolve_target_action(
        cls, screen_state: ParsedScreenState, intent: str
    ) -> Dict[str, Any]:
        """
        Matches a natural language target intent (e.g., "Submit", "Search")
        to the best candidate element in the active screen state.
        """
        intent_clean = intent.lower().strip()

        for element in screen_state.interactive_elements:
            element_text = (element.text or "").lower()
            element_desc = (element.content_desc or "").lower()
            if intent_clean in element_text or intent_clean in element_desc:
                return {
                    "action": "click",
                    "target_type": "element_match",
                    "node_id": element.node_id,
                    "matched_text": element.text or element.content_desc,
                    "center_point": {
                        "x": element.center_point[0],
                        "y": element.center_point[1],
                    },
                }

        return {
            "action": "unknown",
            "target_type": "none",
            "message": (
                f"Target intent '{intent}' not found on screen package "
                f"{screen_state.package_name}"
            ),
        }
