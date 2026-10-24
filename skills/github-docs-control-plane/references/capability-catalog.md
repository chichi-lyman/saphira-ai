# Capability catalog reference

The catalog is how a runtime finds a tool without a database round-trip. One entry per callable skill, endpoint, or adapter.

Look for an existing module before creating one. Likely names: `saphira_capability_catalog.py`, a registry under `packages/saphira_core/`, or a JSON file the runtime already imports. Extend that. A second catalog is a bug.

## Entry schema

```python
# Copyright © 2026 Chelsea Megan Woods
from dataclasses import dataclass

@dataclass(frozen=True)
class Capability:
    id: str                 # kebab-case, stable
    summary: str            # one sentence
    owner: str              # pipeline seat that executes it
    policy: str             # ALLOW | REQUIRE_APPROVAL | DENY
    entrypoint: str         # import path or file path that exists
    inputs: tuple[str, ...]
    side_effects: bool
```

JSON equivalent, if the repo already uses JSON:

```json
{
  "id": "github-docs-control-plane",
  "summary": "Writes and checks Saphira control-plane docs.",
  "owner": "agent-zero",
  "policy": "REQUIRE_APPROVAL",
  "entrypoint": "skills/github-docs-control-plane/SKILL.md",
  "inputs": ["target_file", "change_summary"],
  "side_effects": true
}
```

## Registration rules

- `entrypoint` must be a path you just verified, or a path this same change creates.
- `policy` defaults to `REQUIRE_APPROVAL` when `side_effects` is true.
- `id` never changes once published. Add a new id and mark the old entry `DENY` if the tool is retired.
- Do not register a skill that only restates another skill.
- The catalog change ships in the same commit as the skill or endpoint it describes.

## Lookup order

1. Exact `id` match.
2. Tag / domain match.
3. Refuse and say the tool is not registered. Do not guess an import.

## Starter catalog snippet

```python
CATALOG: tuple[Capability, ...] = (
    Capability(
        id="github-docs-control-plane",
        summary="Maintains governance, copilot instructions, catalog, workflows, and the learning ledger.",
        owner="agent-zero",
        policy="REQUIRE_APPROVAL",
        entrypoint="skills/github-docs-control-plane/SKILL.md",
        inputs=("target_file", "change_summary"),
        side_effects=True,
    ),
)
```
