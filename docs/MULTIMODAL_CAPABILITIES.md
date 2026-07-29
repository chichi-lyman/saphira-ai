# Saphira AI — Core System & Multimodal Capabilities
**Prepared for Chelsea Megan Woods**  
**Copyright © 2026 Chelsea Megan Woods. All Rights Reserved.**  
**System:** saphira-ai

Saphira is the floating **voice, vision, hardware & design orchestrator**. Backend specialists run the work; the Samantha dual pipeline speaks the results.

```
                    SAPHIRA AI
         Floating Voice / Vision / Hardware / Design
              /              |              \
     Real-time voice    Vision & gestures   Parametric 3D
```

## Feature matrix

| Domain | What Saphira executes | Stack |
|--------|----------------------|--------|
| Real-time voice | Low-latency dual-pipeline speech, interrupt-friendly, Samantha cadence | Gemini Native Audio / ElevenLabs (Chelsea voice) |
| Air gestures | Spatial UI — drag, click, release overlays | MediaPipe Hands |
| Biometric auth | Face landmarker for unlock layers / confirm | MediaPipe Face Landmarker |
| Parametric 3D CAD | Voice → editable solid geometry | build123d → STL |
| Wireless slice & print | Discover printers, slice, send job | OrcaSlicer + Klipper/Moonraker/PrusaLink |
| Web automation | Browse, fill, extract | Playwright + Chromium |
| Smart environment | Lights, scenes, power | Home Assistant / Matter / python-kasa |
| Context & memory | Projects, schedules, sandbox, vectors | NovaAethrea + Aura + optional Supabase |

## Capability notes

### 1. Hands-free vision & gestures
- Live camera: people, objects, documents (Aura + ADA bridge)
- Gestures: pinch confirm, fist drag, open palm release (overlay UI)
- L1 actions still need explicit confirm even if face is recognized

### 2. Voice → 3D print
- Verbal brief → Agent Zero / CAD path (build123d)
- Match printer profile → slice → Moonraker/PrusaLink job
- Persona: *"I shaped that bracket and queued it on the printer"* — no agent names

### 3. System & hardware
- *"Focus mode"* → scenes via Matter/HA (L2)
- Web tasks via Playwright in sandbox (L2; L1 if submitting sensitive forms)

## Code anchors

| Module | Role |
|--------|------|
| `src/core/multimodal_registry.py` | Capability flags & routing hints |
| `src/core/ada_bridge.py` | Audio / vision / CAD hooks |
| `src/connectors/matter_home_assistant.py` | Smart environment |
| `src/core/saphira_translator.py` | Warm public output |
| `lib/ui/overlays/saphira_bottom_sheet.dart` | Floating UI |

## Autonomy

| Capability | Default level |
|------------|---------------|
| Chat / explain | L1–L2 |
| Gestures on overlay (non-sensitive) | L2 |
| Face unlock of sensitive layers | L1 |
| CAD generate | L2 |
| Send print job | L2 (L1 if cost gate configured) |
| Web form submit with credentials | L1 |
| Lights / scenes | L2 |
| Memory ingest | L3 |
