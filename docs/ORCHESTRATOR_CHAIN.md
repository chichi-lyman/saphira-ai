# Saphira Orchestrator Chain
**Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.**

## Pipeline Order

```
User voice / text
        ↓
1. Saphira          NLP + intent parsing (regex + phrase map)
        ↓
2. Aura             Perception — room detection + entity suggestions
        ↓
3. Agent Two        Security gate (blocks unlock/lock without confirmation)
        ↓
4. Nova Reign       Governance / policy allow-list
        ↓
5. NovaAethrea      Persistent memory + scene expansion
        ↓
6. Agent Zero       Execution (Matter / Home Assistant / system)
        ↓
Final response + full trace
```

## What Each Agent Contributes

| Step | Agent        | Contribution                                      |
|------|--------------|---------------------------------------------------|
| 1    | Saphira      | Turns natural language into a clean intent        |
| 2    | Aura         | Fills in missing entity_id from room context      |
| 3    | Agent Two    | Stops sensitive actions unless user confirmed     |
| 4    | Nova Reign   | Rejects anything outside approved policy          |
| 5    | NovaAethrea  | Loads scenes from disk + stores facts/history     |
| 6    | Agent Zero   | Calls Home Assistant / Matter devices             |

## Persistent Memory
NovaAethrea writes to `data/nova_aethrea_memory.json`:
- facts
- preferences
- custom scenes
- recent history (last 200 entries)

## Example

User: “Good night”

1. Saphira → intent = activate_scene
2. Aura → no extra entities needed
3. Agent Two → cleared (scene steps will be pre-approved)
4. Nova Reign → approved
5. NovaAethrea → expands “good_night” into 4 device steps
6. Agent Zero → executes each step via Matter/HA
