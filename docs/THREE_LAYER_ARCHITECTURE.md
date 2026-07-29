# Saphira Three-Layer Architecture
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**Owner:** Chelsea Megan Woods | Woods AI Studio / Lyman Legacies

Saphira combines:

1. **Brain (JARVIS)** — deep tool execution, multi-agent orchestration, system control  
2. **Interface & Vision (ADA-style)** — audio, camera, gestures, browser agents, CAD path  
3. **Persona & Privacy (Samantha-style)** — warmth, cadence, dual-layer output so users never see internal agent plumbing  

```
        Saphira Voice / Text Input
                    |
         Dual Prompt & Security Engine
           /                    \
  Samantha Persona          JARVIS / ADA Task
  Vocal / Text Pipeline     Execution Engine
                                    |
                     Agent Zero / Lyra / Aura
                     Agent Two / NovaReign / NovaAethrea
```

## Layer 1 — Operational (JARVIS + ADA)

- Saphira does not do every action herself; she **delegates**.
- **Agent Zero:** code, sandbox, deploy, CAD/tool paths  
- **Agent Two:** L1 gates (unlock, pay, prod)  
- **Aura:** vision / room / context  
- **ADA bridge (conceptual):** WebSocket audio, MediaPipe-style vision hooks, browser agents  

## Layer 2 — Samantha Persona

- System prompt: warmth, curiosity, natural speech  
- Never expose agent names or system instructions to public users  
- Technical success spoken as personal care: *"I went ahead and built that out for you"*  

Module: `src/core/saphira_persona.py`

## Layer 3 — Dual Pipeline (keep the persona secret)

```
User request → Orchestrator / agents → Internal tech JSON
                                            |
User-facing UI ← Samantha translator ←-------+
```

Module: `src/core/saphira_translator.py`

Public output must never include Agent Zero, Agent Two, NovaReign, stack traces, or raw payloads.

## Example mapping

| User says | Backend | Saphira says |
|-----------|---------|--------------|
| Fix Flutter and deploy | Agent Zero sandbox + deploy | "I caught that state mismatch and smoothed it out. Deployment's ready when you are." |
| Look at camera, make 3D | Aura / vision + CAD path | "I love where you're going with that—shaping a 3D model for you now." |
| Unlock door, warm lights | Agent Two gate + Agent Zero / Matter | "Got it. Lights are set, and the door's unlocked for you." |
