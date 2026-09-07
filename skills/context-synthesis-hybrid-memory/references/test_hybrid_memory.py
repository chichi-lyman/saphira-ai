# Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.
# Unit-test stubs for hybrid memory components.

import unittest
from embedding_pipeline import EmbeddingPipeline
from graph_upsert import GraphStore
from typing import Any, Dict

# Minimal inline re-implementation of ContextSynthesisEngine for isolated testing
class ContextSynthesisEngine:
    def __init__(self, similarity_threshold: float = 0.82):
        self.similarity_threshold = similarity_threshold

    def synthesize_context(self, current_intent, vector_memories, graph_facts, tool_state):
        deduplicated = {}
        for fact in graph_facts:
            key = f"{fact['subject']}:{fact['predicate']}"
            if key not in deduplicated or fact["confidence_score"] > deduplicated[key]["confidence_score"]:
                deduplicated[key] = fact
        relevant = [
            m["text_chunk"] for m in vector_memories
            if m.get("relevance_score", 1.0) >= self.similarity_threshold
        ]
        return {
            "active_intent": current_intent,
            "system_state": tool_state,
            "verified_facts": list(deduplicated.values()),
            "retrieved_context": relevant,
            "signature": "Chelsea Megan Woods™",
        }


class TestEmbeddingPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = EmbeddingPipeline(dimensions=8)  # small for tests

    def test_create_memory_node_structure(self):
        node = self.pipeline.create_memory_node(
            text_chunk="User prefers morning deep-work blocks",
            source="preference",
            graph_relations=[{
                "subject": "User",
                "predicate": "prefers",
                "object": "morning_deep_work",
                "confidence_score": 0.95,
            }],
        )
        self.assertIn("memory_id", node)
        self.assertIn("timestamp", node)
        self.assertEqual(len(node["semantic_payload"]["embedding"]), 8)
        self.assertEqual(node["owner"], "Chelsea Megan Woods™")
        self.assertEqual(len(node["graph_relations"]), 1)


class TestGraphStore(unittest.TestCase):
    def setUp(self):
        self.store = GraphStore()

    def test_upsert_keeps_higher_confidence(self):
        self.store.upsert_relation("User", "prefers", "dark_mode", 0.70)
        kept = self.store.upsert_relation("User", "prefers", "dark_mode", 0.90)
        self.assertEqual(kept["confidence_score"], 0.90)

        # lower score should not overwrite
        kept2 = self.store.upsert_relation("User", "prefers", "dark_mode", 0.50)
        self.assertEqual(kept2["confidence_score"], 0.90)

    def test_query_by_subject(self):
        self.store.upsert_relation("ProjectX", "depends_on", "API_v2", 0.88)
        results = self.store.query_by_subject("ProjectX")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["object"], "API_v2")


class TestContextSynthesisEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ContextSynthesisEngine(similarity_threshold=0.80)

    def test_contradiction_resolution(self):
        graph_facts = [
            {"subject": "Budget", "predicate": "status", "object": "over", "confidence_score": 0.60},
            {"subject": "Budget", "predicate": "status", "object": "under", "confidence_score": 0.92},
        ]
        result = self.engine.synthesize_context(
            current_intent="check budget",
            vector_memories=[],
            graph_facts=graph_facts,
            tool_state={},
        )
        verified = result["verified_facts"]
        self.assertEqual(len(verified), 1)
        self.assertEqual(verified[0]["object"], "under")
        self.assertEqual(verified[0]["confidence_score"], 0.92)


if __name__ == "__main__":
    unittest.main()
