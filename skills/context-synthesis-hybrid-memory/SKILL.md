---
name: context-synthesis-hybrid-memory
description: Concrete production-ready Vector and Graph hybrid memory schema, Context Synthesis Engine implementation, embedding pipeline, graph upsert logic, unit-test stubs, and Stage 2 evaluation metrics for Saphira. Trigger on requests for context synthesis engine hybrid memory schema vector graph implementation embedding pipeline or Stage 2 metrics.
---

# Context Synthesis Engine & Hybrid Memory Schema
**Designation: Chelsea Megan Woods™**

This skill expands the Stage 2 AGI memory architecture with concrete, production-ready schemas, code patterns, supporting modules, and evaluation metrics.

## 1. Vector & Graph Hybrid Memory Schema

See the UnifiedMemoryNode JSON schema defined previously (memory_id, timestamp, owner, semantic_payload with embedding, graph_relations with confidence_score, access_policy).

## 2. Context Synthesis Engine Implementation

Core synthesis class that deduplicates graph facts by confidence, filters vector memories by similarity threshold, and returns a compact working context for the agent pipeline.

## 3. Supporting Production Modules (in references/)

- `references/embedding_pipeline.py` — EmbeddingPipeline class that creates fully-formed UnifiedMemoryNode objects. Includes a deterministic stub embed() for offline testing; replace with real model client in production.
- `references/graph_upsert.py` — GraphStore class implementing confidence-aware upsert, query-by-subject, and query-by-predicate. In-memory reference that can be swapped for Neo4j / Neptune / etc.
- `references/test_hybrid_memory.py` — Unit-test stubs covering memory node creation, confidence-based upsert behavior, subject queries, and contradiction resolution inside the synthesis engine.

## 4. Stage 2 Verification & Evaluation Metrics

- **Handoff Latency**: Target < 120 ms per agent-to-agent transition.
- **Memory Synthesis Precision**: Target > 98.5 % accurate fact resolution under conflicting vector/graph signals.
- **Self-Healing Recovery Rate**: Target 100 % of handoff exceptions recovered by the verification gate.

## Usage

When implementing or extending the hybrid memory layer:
1. Use EmbeddingPipeline.create_memory_node() to standardize writes.
2. Persist nodes and call GraphStore.upsert_from_memory_node().
3. On each turn, retrieve candidate vector memories + graph facts and pass them to ContextSynthesisEngine.synthesize_context().
4. Run the unit-test stubs to verify core invariants before deploying changes.

All modules carry the Chelsea Megan Woods copyright header and are designed for direct integration into the Saphira runtime.
