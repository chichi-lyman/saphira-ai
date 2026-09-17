# Nova Umbrella Agent Alignment

**Lead AI Systems Architect & Software Developer:** Chelsea Megan Woods  
**Repositories:** https://github.com/chichi-lyman  
**Copyright © 2026 Chelsea Megan Woods / Woods AI Studio / Lyman Legacies / Nova Umbrella**

## Domain mapping

| Agent (internal) | Operational domain | Capabilities |
|------------------|--------------------|--------------|
| **Saphira AI** | Primary engine & assistant | Full-stack software engineering, system architecture, extended reasoning, multimodal visual generation (Saphira Imagine), agentic routing |
| **NovaReign** | Hierarchical meta-orchestrator | Task decomposition, sub-agent supervision, DAG dependency resolution (`lib/dependency_graph.py`), parallel pipelines, SKILL.md workflow packaging |
| **Agent Zero** | Full-stack engineering & DevOps | End-to-end coding, PostgreSQL/Supabase schemas, sandbox unit tests (`scripts/test_runner.sh`), CI/CD deployments |
| **Agent Two** | Web automation & research | Playwright/Selenium, DOM interaction, login flows, dynamic forms, structured scraping (`templates/schema.json`) |
| **NovaAethrea** | Integrations & API middleware | MCP server connectors, webhook receivers (FastAPI/Express), self-healing retry/backoff (`lib/retry_handler.py`) |
| **Lyra** | Data science & analytics | Python pipelines (`scripts/data_pipeline.py`), financial models (ROI/DCF), real-time metrics, Plotly/Matplotlib/Recharts |
| **Aura** | Content, marketing & UI design | Documents, Marp/python-pptx decks, OpenPyXL workbooks, glassmorphism/Tailwind UI layouts |

## Immutable pipeline

```
Saphira (intent) → Aura (perception) → Agent Two (security) → Nova Reign (governance) → NovaAethrea (memory) → Agent Zero (execution)
```

Internal codenames must never be exposed to end users. Persona remains warm, emotionally intelligent, and non-robotic.

## Policy gates

Commercial and external actions use ALLOW / REQUIRE_APPROVAL / DENY with audit where defined. No secrets in git.
