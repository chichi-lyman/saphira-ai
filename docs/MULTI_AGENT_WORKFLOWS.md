# Multi-Agent Workflows

**Copyright © 2026 Chelsea Megan Woods**  
**System:** saphira-ai

Concrete implementation of the **Creation → Live Usage** multi-agent axis from [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md).

## What shipped

| Piece | Path |
|-------|------|
| DAG workflow engine | `src/orchestration/multi_agent_workflow.py` |
| Skill-backed workers | `src/orchestration/workers.py` |
| Custom agent skills | `skills/saphira-code-reviewer/`, `skills/saphira-systems-architect/`, `skills/saphira-data-analyst/` |
| Tests | `tests/test_multi_agent_workflow.py` |

## Engine capabilities

- **WorkflowGraph** — nodes with `depends_on` and optional `parallel_group`
- **Templates**
  - `build_research_code_validate` — research ‖ draft → implement → validate
  - `build_analyze_architect_review` — data ‖ architecture ‖ code review → synthesize
  - `build_custom_linear` — arbitrary linear chains
- **MultiAgentWorkflowEngine** — routes capabilities via `AgentRegistry`, runs ready nodes in parallel (semaphore-bounded), records structured handoff envelopes, merges artifacts into a `Task`
- **HandoffEnvelope** — internal only; aligns with [AGENT_INTERACTION_PROTOCOLS.md](./AGENT_INTERACTION_PROTOCOLS.md)

## Custom agent skills (sub-personas)

These are system-prompt architectures registered as skills. Users only ever talk to **Saphira**; the skills guide background workers.

### 1. Saphira Code Reviewer — `skills/saphira-code-reviewer/`

- Correctness, security, style, tests
- Worker: `code_reviewer_agent` (`CodeReviewerWorker`)
- Capabilities: `code_review`, `development`, `quality`

### 2. Saphira Systems Architect — `skills/saphira-systems-architect/`

- Component boundaries, pipeline layout, reliability
- Worker: `systems_architect_agent` (`SystemsArchitectWorker`)
- Capabilities: `architecture`, `system`, `development`

### 3. Saphira Data Analyst — `skills/saphira-data-analyst/`

- Metrics, trends, caveats, chart guidance
- Worker: `data_analyst_agent` (`DataAnalystWorker`)
- Capabilities: `analytics`, `research`, `stem`

Each `SKILL.md` follows agentskills.io frontmatter rules and the secret-mask invariant.

## Quick usage

```python
from src.orchestration.multi_agent_workflow import MultiAgentWorkflowEngine
from src.orchestration.workers import default_workers
from src.orchestration.executor import TaskExecutor

workers = default_workers()
engine = MultiAgentWorkflowEngine(executor=TaskExecutor(workers=workers))

task, graph = await engine.run_research_code_validate(
    "Add a health endpoint and tests"
)
assert task.status.value == "completed"
```

Or the architect / analyst fan-out:

```python
task, graph = await engine.run_analyze_architect_review(
    "Review the multi-agent pipeline and propose metrics"
)
```

## Pipeline alignment

Workflows are planned under **Nova Reign** (governance), executed by workers that map to Agent Zero / Lyra / specialist lanes, and always surface through **Saphira**. Internal agent and skill names never appear in user-facing text.

## Related

- [SUPER_FEATURES_FRAMEWORK.md](./SUPER_FEATURES_FRAMEWORK.md)
- [AGENT_SKILL_FRAMEWORK.md](./AGENT_SKILL_FRAMEWORK.md)
- [AGENT_INTERACTION_PROTOCOLS.md](./AGENT_INTERACTION_PROTOCOLS.md)
- [ORCHESTRATOR_CHAIN.md](./ORCHESTRATOR_CHAIN.md)
