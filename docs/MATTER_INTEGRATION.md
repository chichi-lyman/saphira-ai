# Matter + Home Assistant Integration for Saphira
**Copyright (c) 2026 Chelsea Megan Woods. All Rights Reserved.**

## Architecture

```
User → Saphira (intent)
         ↓
    Agent Two (security gate)
         ↓
    Nova Reign (governance)
         ↓
    Agent Zero (execution)
         ↓
    MatterHomeAssistantConnector
         ↓
    Home Assistant REST API
         ↓
    Matter devices (lights, locks, climate, covers…)
```

## Environment Variables

```
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=your_long_lived_access_token
```

## Supported Intents (via Agent Zero)

| Intent            | Example params                                      |
|-------------------|-----------------------------------------------------|
| turn_on / on      | entity_id=light.living_room                         |
| turn_off / off    | entity_id=light.kitchen                             |
| toggle            | entity_id=switch.fan                                |
| set_brightness    | entity_id=light.bedroom, brightness_pct=30          |
| set_temperature   | entity_id=climate.main, temperature=72              |
| lock / unlock     | entity_id=lock.front_door (requires confirmation)   |
| set_cover         | entity_id=cover.blinds, position=50                 |

## Agent Responsibilities

- **Saphira** — parses voice/text into intent + params
- **Agent Two** — blocks sensitive actions (unlock) without confirmation
- **Nova Reign** — policy / boundary check
- **Agent Zero** — calls the Matter/HA connector
- **Aura** — can supply room / device context from vision
- **Nova Etherea** — remembers preferred scenes and device names
