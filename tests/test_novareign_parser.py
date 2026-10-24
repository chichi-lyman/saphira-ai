# Copyright (c) 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella
# All rights reserved.

"""Verification tests for NovaReignScreenParser bounds and intent resolution."""

from __future__ import annotations

import pytest

from src.core.novareign_a11y_parser import (
    NovaReignScreenParser,
    ParsedScreenState,
    UINode,
)


SAMPLE_TREE = {
    "package_name": "com.example.searchapp",
    "root_node": {
        "class_name": "android.widget.FrameLayout",
        "bounds": [0, 0, 1080, 2400],
        "children": [
            {
                "class_name": "android.widget.EditText",
                "text": "Search",
                "content_desc": "Search field",
                "is_clickable": True,
                "is_editable": True,
                "is_focused": True,
                "view_id_resource_name": "com.example:id/search_box",
                "bounds": [40, 120, 1040, 220],
                "children": [],
            },
            {
                "class_name": "android.widget.Button",
                "text": "Submit",
                "content_desc": "Submit query",
                "is_clickable": True,
                "is_editable": False,
                "view_id_resource_name": "com.example:id/submit_btn",
                "bounds": [400, 300, 680, 400],
                "children": [],
            },
            {
                "class_name": "android.widget.ScrollView",
                "is_scrollable": True,
                "bounds": [0, 450, 1080, 2000],
                "children": [],
            },
            {
                "class_name": "android.view.View",
                "bounds": [0, 0, 0, 0],
                "children": [],
            },
        ],
    },
}


def test_calculate_center():
    assert NovaReignScreenParser.calculate_center((0, 0, 100, 50)) == (50, 25)
    assert NovaReignScreenParser.calculate_center((40, 120, 1040, 220)) == (540, 170)


def test_parse_raw_tree_extracts_interactive_and_focused():
    state = NovaReignScreenParser.parse_raw_tree(SAMPLE_TREE)

    assert isinstance(state, ParsedScreenState)
    assert state.package_name == "com.example.searchapp"
    assert len(state.interactive_elements) >= 2
    assert state.focused_input is not None
    assert state.focused_input.node_id == "com.example:id/search_box"
    assert state.focused_input.center_point == (540, 170)

    texts = {(e.text or "").lower() for e in state.interactive_elements}
    assert "search" in texts
    assert "submit" in texts

    assert len(state.scrollable_elements) >= 1


def test_parse_empty_tree():
    state = NovaReignScreenParser.parse_raw_tree({"package_name": "empty.app"})
    assert state.package_name == "empty.app"
    assert state.interactive_elements == []
    assert state.focused_input is None


def test_resolve_target_action_matches_submit():
    state = NovaReignScreenParser.parse_raw_tree(SAMPLE_TREE)
    plan = NovaReignScreenParser.resolve_target_action(state, "Submit")

    assert plan["action"] == "click"
    assert plan["target_type"] == "element_match"
    assert plan["node_id"] == "com.example:id/submit_btn"
    assert plan["center_point"]["x"] == 540
    assert plan["center_point"]["y"] == 350


def test_resolve_target_action_matches_search_case_insensitive():
    state = NovaReignScreenParser.parse_raw_tree(SAMPLE_TREE)
    plan = NovaReignScreenParser.resolve_target_action(state, "search")

    assert plan["action"] == "click"
    assert plan["target_type"] == "element_match"
    assert "search" in (plan.get("matched_text") or "").lower()


def test_resolve_target_action_unknown_intent():
    state = NovaReignScreenParser.parse_raw_tree(SAMPLE_TREE)
    plan = NovaReignScreenParser.resolve_target_action(state, "NonexistentButton")

    assert plan["action"] == "unknown"
    assert plan["target_type"] == "none"
    assert "NonexistentButton" in plan["message"]


def test_zero_bounds_nodes_excluded():
    state = NovaReignScreenParser.parse_raw_tree(SAMPLE_TREE)
    for el in state.interactive_elements:
        assert el.bounds_in_screen != (0, 0, 0, 0)
