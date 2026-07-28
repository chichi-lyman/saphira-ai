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
    NovaAethrea (scenes / memory)
         ↓
    Agent Zero (execution)
         ↓
    MatterHomeAssistantConnector
         ↓
    Home Assistant REST + WebSocket
         ↓
    Matter devices
```

## Environment Variables

```
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=your_long_lived_access_token
```

## Supported Intents

| Intent | Params | Cluster / Domain |
|--------|--------|------------------|
| turn_on / on | entity_id | OnOff |
| turn_off / off | entity_id | OnOff |
| toggle | entity_id | OnOff |
| set_brightness / dim | entity_id, brightness_pct | LevelControl |
| set_color | entity_id, rgb / kelvin / hs | ColorControl |
| set_temperature | entity_id, temperature | Thermostat |
| set_hvac_mode | entity_id, mode | Thermostat |
| set_fan_mode | entity_id, fan_mode | Fan |
| fan_percentage | entity_id, percentage | Fan |
| fan_preset | entity_id, preset | Fan |
| lock / unlock | entity_id | DoorLock |
| set_cover / open_cover / close_cover | entity_id, position | WindowCovering |
| media_play / pause / stop | entity_id | Media |
| media_volume | entity_id, volume (0-1) | Media |
| activate_scene | entity_id (scene.xxx) | Scene |

## WebSocket Live State

```python
from src.connectors.matter_home_assistant import matter_ha

def on_state_change(entity_id, state):
    print(entity_id, state["state"], state.get("attributes"))

matter_ha.add_state_listener(on_state_change)
matter_ha.start_websocket()
```

Cached states are available via `matter_ha.get_cached_state("light.living_room")`.

## Dependency

```
pip install websocket-client requests
```
