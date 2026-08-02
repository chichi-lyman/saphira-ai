# Saphira Nodes
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Saphira Nodes are the physical **eyes, ears, hands, and screens** for your central AI agent gateway — the same conceptual model as OpenClaw Nodes, implemented natively for Saphira’s multi-agent pipeline.

Instead of only returning text, a node lets Saphira create files, local environments, automated workflows, visual surfaces, and sensory inputs directly on your devices.

```
                    Saphira Gateway (orchestrator)
                              |
              +---------------+---------------+
              |               |               |
         Headless/VS Code   Canvas/Media    Mobile Nodes
         (code, PRs, envs)  (dashboards,    (camera, SMS,
                             viz, video)     location, notifs)
```

## Node types

| Type | Role | Primary capabilities |
|------|------|----------------------|
| `headless` | CLI / server process | code.read/write/exec/test/pr/env, system.exec |
| `vscode` | IDE-aware extension | deep workspace + test + PR surface |
| `canvas` | Desktop / web visual host | present, navigate, eval, snapshot, a2ui, dashboard |
| `media` | Local render host | viz, video intros, asset render |
| `mobile_ios` | iOS companion | camera, location, notifications, light canvas |
| `mobile_android` | Android companion | camera, location, notifications, SMS, system.exec |

## What each family can build

### 1. Code, websites, and software (Headless / VS Code)
- Complete repositories: read workspace, write scripts, scaffold sites, init pipelines
- Automated PRs: run local tests, push branches, open PRs
- Local DB & server environments on demand (e.g. via messaging)

### 2. Animated videos & digital assets (Media)
- Dynamic data visualizations → polished animated charts
- Short programmatic video clips (intros with text, gradients, fades)

### 3. Native interfaces & UI (Canvas)
- Mission-control dashboards aggregating calendar / Notion / todos
- Visual briefings as interactive cards instead of paragraphs
- A2UI-style surface pushes

### 4. System automation & physical inputs (Mobile)
- Live camera + screen + location feeds for Aura (perception)
- Native notifications, background SMS (Android, gated), remote system commands

## Pairing flow

1. Device or process registers → status `pending`
2. Approve via API or future CLI (`POST /nodes/{id}/approve`)
3. Node becomes `online` and accepts `node.invoke` commands
4. Agent Zero / orchestrator routes work with capability checks + optional allowlists

## API surface (FastAPI)

```
GET    /nodes                  — list nodes (filter by status / type)
POST   /nodes/register         — register / re-register a node
POST   /nodes/{id}/approve     — approve pairing
POST   /nodes/{id}/reject      — reject pairing
DELETE /nodes/{id}             — remove node
GET    /nodes/status           — summary counts
POST   /nodes/invoke           — invoke command on a specific node
POST   /nodes/invoke-any       — pick best online node for a capability
```

## Invoke examples

```json
// Camera snap on a mobile node
POST /nodes/invoke
{
  "node": "chelsea-iphone",
  "command": "camera.snap",
  "params": { "facing": "front", "maxWidth": 1280 }
}

// Spin up a dashboard on a canvas node
POST /nodes/invoke-any
{
  "command": "canvas.dashboard",
  "params": {
    "title": "Morning Briefing",
    "sources": ["calendar", "notion", "todos"]
  }
}

// Scaffold a local env on a headless node
POST /nodes/invoke
{
  "node": "dev-laptop",
  "command": "code.env",
  "params": { "name": "saphira-dev", "services": ["postgres", "redis"] }
}
```

## Integration with Saphira agents

| Agent | Node interaction |
|-------|------------------|
| **Aura** | Consumes `camera.*` / screen / location feeds |
| **Agent Zero** | Executes `code.*`, `system.exec`, CAD/print paths on capable nodes |
| **NovaAethrea** | Stores node identities & preferred devices in long-term memory |
| **Agent Two** | Gates sensitive system / SMS / unlock-class actions |
| **Saphira persona** | Speaks results warmly — never exposes node IDs or raw payloads |

## Code layout

```
src/nodes/
  __init__.py
  base.py          # Node, NodeType, NodeCapability, defaults
  registry.py      # Pairing, lookup, capability search
  invoke.py        # Routing + safety checks
  handlers/
    code_handler.py
    media_handler.py
    canvas_handler.py
    camera_handler.py
    system_handler.py
```

Handlers currently return structured **simulation** results so the rest of the stack can be developed against a stable contract. Real companion apps (Flutter Android already present in-repo, future iOS / headless CLI) replace the simulation layer with local device APIs while keeping the same command surface.

## Security notes

- Only `online` nodes accept invokes
- Capability check + optional per-node allowlist
- Sensitive actions (SMS, unlock-class system commands) still pass through Agent Two confirmation
- Camera / canvas foreground requirements apply on real mobile nodes (background → `NODE_BACKGROUND_UNAVAILABLE`)

---

*Saphira Nodes bring OpenClaw-class physical agency into the Saphira ecosystem while preserving the Samantha dual-pipeline persona and the six-core agent chain.*
