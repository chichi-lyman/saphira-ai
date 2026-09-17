# Agent Skill Framework (Manus-aligned)

Saphira and the Nova Umbrella use executable **SKILL.md** bundles (open Agent Skills style) to standardize how domain agents operate, reason, and interface with tools.

## Categories of autonomous sub-agents

1. **Browser automation & web scraper** (Agent Two) — navigate live pages, forms, login flows, structured extract  
2. **Full-stack software engineering & DevOps** (Agent Zero / Saphira) — frontend, APIs, schemas, tests, deploy  
3. **Integrations & MCP connectors** (NovaAethrea) — MCP, webhooks, self-healing recovery  
4. **Data analysis & financial research** (Lyra) — market data, models, charts  
5. **Document & presentation automation** (Aura) — reports, Excel, slide decks  
6. **Hierarchical meta-orchestrator** (NovaReign) — decompose objectives, assign sub-agents, parallel pipelines  

## Skill package shape

Each skill is a directory:

```
skill-name/
├── SKILL.md           # frontmatter + imperative instructions
├── scripts/           # Playwright, test_runner, data_pipeline, retry_handler, etc.
├── references/        # domain docs loaded on demand
└── assets/            # templates, schema.json, CSS, charts stubs
```

Frontmatter rules (agentskills.io):

- `name` kebab-case, matches directory  
- `description` plain YAML scalar (no `: `, no `<` `>`, single line, ≤1024 chars)  
- Custom fields under `metadata:` only  

## Advanced skill types by category

### Web automation & research
- Dynamic UI form & action drivers  
- Structured web scraping & extraction  
- Competitor & market intelligence pipelines  
- Assets: Playwright/Selenium scripts, session/cookie handlers, `templates/schema.json`  

### Full-stack engineering & DevOps
- Autonomous app architecture & schema builders  
- Self-debugging & test execution engines  
- Deployment & CI/CD automation  
- Assets: migration blueprints, `scripts/test_runner.sh`, Vite/Vercel build scripts  

### Integrations & MCP
- MCP server connectors  
- Automated webhook & API middleware  
- Self-healing error recovery loops  
- Assets: MCP manifests, FastAPI/Express receivers, `lib/retry_handler.py`  

### Data science & finance
- Automated data processing & Python analysis  
- Real-time financial & metric monitoring  
- Dynamic visualization & reporting  
- Assets: `scripts/data_pipeline.py`, chart generators, DCF/ROI templates  

### Content, marketing & UI
- Automated document & deck generators  
- Multi-channel media scripting  
- Design & layout engineering  
- Assets: python-pptx/Marp, OpenPyXL builders, glassmorphism/Tailwind patterns  

### Meta-orchestration
- Sub-agent task decomposition  
- One-click workflow packaging (SKILL.md synthesis from run logs)  
- Parallel execution pipelines  
- Assets: `lib/dependency_graph.py`, parallel drivers  

## Grok out-of-the-box capabilities used in this ecosystem

- DeepSearch & real-time synthesis  
- Extended reasoning (complex math, architecture planning)  
- Image generation and multi-turn editing  
- Sandboxed code execution and automated debugging  
- Agentic tool calling (APIs, databases, third-party workflows)  

## Related docs

- [AGENT_ALIGNMENT.md](./AGENT_ALIGNMENT.md) — domain agent map  
- [EVOLUTIONARY_ARCHITECTURE.md](./EVOLUTIONARY_ARCHITECTURE.md) — self-heal / optimise loop  
- Repository skill mirror: `skills/woods-multi-agent/`  
