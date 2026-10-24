# Offline RAG for Localized Spark

**Copyright © 2026 Chelsea Megan Woods**  
**Parent:** [FIELD_MANUAL_CORPUS.md](./FIELD_MANUAL_CORPUS.md) · [LOCALIZED_SPARK_PROTOCOL.md](./LOCALIZED_SPARK_PROTOCOL.md)

## Pipeline

1. **Acquire** — only public FMs / FEMA / data.gov releases  
2. **Extract** — PDF → clean text  
3. **Chunk** — 500–1000 tokens with headers (`source`, `designator`, `topic`)  
4. **Embed** — local model  
5. **Store** — on-device vector DB  
6. **Query** — offline LLM + retrieved passages  
7. **Gate** — logic + humility: no hallucinated “classified” facts; no sovereign triage  

## Metadata schema (chunk)

```json
{
  "designator": "FM 3-05.70",
  "topic": "water_procurement",
  "source_url": "https://...",
  "classification": "unclassified_public",
  "pack": "wilderness"
}
```

## Runtime sketch

- Module path (future): `src/orchestration/spark_rag.py`  
- Capability keys: `weaver.crisis_synth`, `foundations.explain`, offline memory read  
- Agent Zero owns install; NovaAethrea owns retention policy  

## Test idea

Given dictation: “flood wall failing, temp dropping, one thigh laceration”—retrieve TCCC hemorrhage principles + structural/flood reasoning + cold stress; output ordered steps with source designators; defer ethics to humans.
