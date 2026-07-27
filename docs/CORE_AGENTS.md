# Saphira Core Six Agents — Highest State
**Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.**

Correct spelling: **NovaAethrea**

## Agents

1. **Saphira** — Command core + tight voice-intent mapping
2. **Agent Zero** — Execution engine (Matter/HA + system actions)
3. **Agent Two** — Security gate (blocks unlock/lock without confirmation)
4. **Aura** — Perception + room/entity suggestions
5. **Nova Reign** — Governance / policy boundary
6. **NovaAethrea** — Persistent memory + scene system (evening, good_night, movie, im_home)

## Self-Healing
Every agent inherits `SelfHealingAgent`:
- Up to 3 retries with exponential backoff
- Returns a safe recovered state instead of crashing
- Logs failures for later upgrade cycles

## Voice → Intent Examples
| Spoken phrase              | Intent            |
|----------------------------|-------------------|
| “dim the lights”           | set_brightness    |
| “lock the front door”      | lock              |
| “good night”               | activate_scene    |
| “set the thermostat to 72” | set_temperature   |
| “I’m home”                 | activate_scene    |

## Scene System (NovaAethrea)
Pre-loaded scenes: `evening`, `good_night`, `movie`, `im_home`
Each scene expands into ordered device steps executed by Agent Zero after security + governance checks.
